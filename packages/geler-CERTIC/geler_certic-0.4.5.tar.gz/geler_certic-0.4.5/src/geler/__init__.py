from typing import Union, Dict, List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin, ParseResult, parse_qs
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from functools import cache
import logging
import requests
import os
import json
import mimetypes
import cssutils
from time import sleep
from base64 import urlsafe_b64encode
from xml.dom import SyntaxErr as XmlDomSyntaxErr

cssutils.log.setLevel(logging.CRITICAL)
logger = logging.Logger(__name__)

SAFE_EXTENSIONS = [".zip", ".md", ".woff", ".woff2", ".htm"]


def parse_css(content: str) -> Union[cssutils.css.cssstylesheet.CSSStyleSheet, None]:
    try:
        css: cssutils.css.cssstylesheet.CSSStyleSheet = cssutils.parseString(content)
        return css
    except XmlDomSyntaxErr as e:  # cssutils fail ?
        logger.error(e)
        return None


def url64(s: Union[dict, str]) -> str:
    if isinstance(s, dict):
        s = json.dumps(s, sort_keys=True).encode()
    if isinstance(s, str):
        s = s.encode()
    return urlsafe_b64encode(s).decode().rstrip("=")


@cache
def guess_extension(mime_type: str) -> str:
    extension = mimetypes.guess_extension(mime_type)
    if extension:
        return extension
    else:
        return ""


@cache
def url_to_path(url: str, mime: str = "") -> str:
    index = ""
    parsed_url = cached_urlparse(url)
    path_no_ext, ext = os.path.splitext(parsed_url.path)
    guessed_ext = ""
    if ext.lower() not in SAFE_EXTENSIONS:
        guessed_ext = guess_extension(mime)
    def_path = path_no_ext
    def_ext = ext
    if guessed_ext and guessed_ext.lower() != ext.lower():
        # keeping original file ext and guessed extension
        # ie. thing.php.html
        def_path = path_no_ext + ext
        def_ext = guessed_ext
    if parsed_url.path.endswith("/"):
        index = "index"
    query_digest = ""
    if parsed_url.query:
        query_digest = "-" + url64(dict(parse_qs(parsed_url.query)))
    result = f"{def_path}{index}{query_digest}{def_ext}"
    return result


@cache
def rebuild_link(parsed_url: ParseResult) -> str:
    return (
        parsed_url.path
        + ("?" + parsed_url.query if parsed_url.query else "")
        + ("#" + parsed_url.fragment if parsed_url.fragment else "")
    )


@cache
def cached_urlparse(url):
    return urlparse(url)


class Freezer:
    def __init__(
        self,
        start_from: str,
        destination: Union[Path, str],
        http_get_timeout: int = 30,
        thread_pool_size: int = 1,
        user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
        keep_alive: bool = True,
        skip_extensions: List[str] = None,
        callback_before_save=None,
        callback_after_save=None,
        callback_after_patch=None,
        dry_run: bool = False,
        callback_before_url_validate=None,
    ):
        self.destination = Path(destination)
        self.write_to_disk = not dry_run
        if not self.destination.exists() and self.write_to_disk:
            os.makedirs(self.destination, exist_ok=True)
        self.start_from_url = start_from.split("#")[0]  # ignore anchors
        parsed_url = cached_urlparse(self.start_from_url)
        if not parsed_url.path:
            self.start_from_url = self.start_from_url + "/"
        self.start_from = parsed_url.netloc
        self.http_get_timeout = http_get_timeout
        self.thread_pool_size = thread_pool_size
        self._html_mimes = ["text/html", "application/xhtml+xml", "application/xml"]
        self._schemes = ["http", "https"]
        self._scrap_executor_pool = ThreadPoolExecutor(
            max_workers=self.thread_pool_size
        )
        self._patch_executor_pool = ThreadPoolExecutor(max_workers=10)
        self._links_done = {}
        self._links_to_do = []
        self.user_agent = user_agent
        self.skip_extensions = []
        if skip_extensions is not None:
            self.skip_extensions = skip_extensions
        self._requests_session = requests.Session()
        self._requests_session.keep_alive = keep_alive
        self.callback_before_save = callback_before_save
        self.callback_after_save = callback_after_save
        self.callback_after_patch = callback_after_patch
        self.callback_before_url_validate = callback_before_url_validate
        self.http_errors = []

    @cache
    def validate_candidate_url(
        self, url: str, parent_url: str
    ) -> Union[ParseResult, bool]:
        if self.callback_before_url_validate:
            self.callback_before_url_validate(url, parent_url)
        if not url.strip():
            return False
        # exclude absolute links not in the site
        if (
            url.startswith("http://") or url.startswith("https://")
        ) and not url.startswith(self.start_from_url):
            return False  # Skip foreign URL
        url_to_join = parent_url
        if url.startswith("/"):
            parsed_parent_url = cached_urlparse(parent_url)
            url_to_join = parsed_parent_url.scheme + "://" + parsed_parent_url.netloc
        url = urljoin(url_to_join, url)  # make link absolute
        parsed_url = cached_urlparse(url)
        if parsed_url.scheme not in self._schemes:  # excludes non http protocols
            return False
        if parsed_url.netloc != self.start_from:
            return False
        _, ext = os.path.splitext(parsed_url.path)
        if ext.lower() in self.skip_extensions:  # exclude extensions
            return False
        url_no_anchor = url.split("#")[0]  # ignore anchors for to do/done lists
        if (
            url_no_anchor not in self._links_done.keys()
            and url_no_anchor not in self._links_to_do
        ):  # Not in queue, submit to executor
            self._scrap_executor_pool.submit(self.scrap_item, url_no_anchor)
            self._links_to_do.append(url_no_anchor)
        else:  # Already in queue, nothing to do here
            pass
        return parsed_url

    def _log_requests_error(self, url: str, response: requests.Response):
        self.http_errors.append(
            {
                "url": url,
                "status_code": response.status_code,
                "content": response.text,
            }
        )

    def scrap_item(self, item_url):
        parts = item_url.split("#")
        item_url_no_anchor = parts[0]

        # add to links in done list early, avoid race conditions
        if item_url_no_anchor not in self._links_done.keys():
            self._links_done[item_url_no_anchor] = ""
        else:
            return
        try:
            response = self._requests_session.get(
                item_url_no_anchor,
                allow_redirects=True,
                timeout=self.http_get_timeout,
                headers={"User-Agent": self.user_agent},
                stream=True,
            )
            if not response.ok:
                self._log_requests_error(item_url_no_anchor, response)
                return
            content_type = (
                response.headers.get("Content-Type", "").split(";")[0].strip()
            )
            self._links_done[item_url_no_anchor] = url_to_path(
                item_url_no_anchor, content_type
            )
            #
            #   Parse and write HTML files
            #
            if content_type in self._html_mimes:
                soup = BeautifulSoup(response.content, "html.parser")
                for attrib in ["href", "src"]:
                    for link in soup.select(f"[{attrib}]"):
                        validated_link = self.validate_candidate_url(
                            link.get(attrib), item_url_no_anchor
                        )
                        if validated_link:
                            link[attrib] = rebuild_link(validated_link)
                # Support <style> tags
                for style_tag in soup.select("style"):
                    css = parse_css(style_tag.text)
                    if css is not None:
                        css_as_string = str(style_tag.text)
                        for url in set(cssutils.getUrls(css)):
                            if not url.startswith("data:"):
                                validated_link = self.validate_candidate_url(
                                    url, item_url_no_anchor
                                )
                                if validated_link:
                                    css_as_string = css_as_string.replace(
                                        url,
                                        rebuild_link(validated_link),
                                    )
                        style_tag.string = css_as_string
                self._save_item_to_disk(item_url_no_anchor, content_type, soup)
            #
            #    Parse and write  CSS files
            #
            elif content_type == "text/css":
                css = parse_css(response.content)
                if css is not None:
                    css_as_string = response.content.decode(css.encoding)
                    for url in set(cssutils.getUrls(css)):
                        if not url.startswith("data:"):
                            validated_link = self.validate_candidate_url(
                                url, item_url_no_anchor
                            )
                            if validated_link:
                                css_as_string = css_as_string.replace(
                                    url,
                                    rebuild_link(validated_link),
                                )
                    self._save_item_to_disk(
                        item_url_no_anchor, content_type, css_as_string
                    )
                else:
                    self._save_item_to_disk(item_url_no_anchor, content_type, response)
            else:
                self._save_item_to_disk(item_url_no_anchor, content_type, response)
        except RequestException as e:
            logger.warning(f"RequestException on URL {item_url_no_anchor}: {e}")
        # whatever happens, remove item from to do list
        finally:
            while item_url_no_anchor in self._links_to_do:
                self._links_to_do.remove(item_url_no_anchor)

    def _save_item_to_disk(
        self,
        item_url: str,
        content_type: str,
        data: Union[requests.Response, BeautifulSoup, str],
    ):
        if self.callback_before_save:
            self.callback_before_save(item_url, content_type, data)
        path_from_url = url_to_path(item_url, content_type)
        local_path = Path(self.destination, path_from_url.lstrip("/"))
        if self.write_to_disk:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            logger.debug(f"Saving {item_url} to {local_path}")
            if type(data) is BeautifulSoup or type(data) is str:
                with open(local_path, "w") as f:
                    f.write(str(data))

            if type(data) is requests.Response:
                with open(local_path, "wb") as f:
                    f.write(data.content)

        # update done list with new URL value
        self._links_done[item_url] = path_from_url

        if self.callback_after_save:
            self.callback_after_save(local_path)

    def _patch_links(self):
        logger.debug("Patching files...")
        parsed_start_url = cached_urlparse(self.start_from_url)
        trans_table = {}
        for original_url, local_path in self._links_done.items():
            url_no_netloc = original_url.split(parsed_start_url.netloc)[1]
            trans_table[url_no_netloc] = local_path
        for _, local_path in self._links_done.items():
            if local_path.endswith(".html") or local_path.endswith(".htm"):
                self._patch_executor_pool.submit(
                    self._patch_html_file, local_path, trans_table
                )
            if local_path.endswith(".css"):
                self._patch_executor_pool.submit(
                    self._patch_css_file, local_path, trans_table
                )
        self._patch_executor_pool.shutdown(wait=True)
        logger.debug("Done patching files.")

    def _patch_css_file(
        self, local_path: Union[Path, str], trans_table: Dict[str, str]
    ) -> bool:
        f_path = Path(self.destination, local_path.lstrip("/"))
        if self.write_to_disk:
            with open(f_path, "r+") as fp:
                content = fp.read()
                for old, new in trans_table.items():
                    if new and (old in content) and old != "/":  # brittle
                        new = os.path.relpath(new, os.path.dirname(local_path))
                        content = content.replace(old, new)
                fp.seek(0)
                fp.write(content)
                fp.truncate()
        if self.callback_after_patch:
            self.callback_after_patch(local_path)
        return True

    def _patch_html_file(self, local_path: Union[Path, str], trans_table: dict) -> bool:
        f_path = Path(self.destination, local_path.lstrip("/"))
        if self.write_to_disk:
            with open(f_path, "r+") as fp:
                soup = BeautifulSoup(fp, "html.parser")
                for attrib in ["href", "src"]:
                    for link in soup.select(f"[{attrib}]"):
                        parts = link.get(attrib).split("#")
                        if parts[0] in trans_table.keys():
                            trans = trans_table[parts[0]].strip()
                            if trans:
                                link[attrib] = os.path.relpath(
                                    trans, os.path.dirname(local_path)
                                ) + ("#" + parts[1] if len(parts) > 1 else "")
                fp.seek(0)
                fp.write(str(soup))
                fp.truncate()
        if self.callback_after_patch:
            self.callback_after_patch(local_path)
        return True

    def freeze(self):
        self.scrap_item(self.start_from_url)
        while len(self._links_to_do) > 0:
            sleep(1)
        self._scrap_executor_pool.shutdown(wait=True)
        self._patch_links()


def freeze(
    start_from_url: str,
    save_to_path: Union[Path, str],
    thread_pool_size: int = 1,
    http_get_timeout: int = 30,
) -> Freezer:
    f = Freezer(
        start_from_url,
        save_to_path,
        thread_pool_size=thread_pool_size,
        http_get_timeout=http_get_timeout,
    )
    f.freeze()
    return f
