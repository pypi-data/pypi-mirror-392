import logging
import argh
import geler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def before_save(item_url, content_type, data):
    logger.info(f"save {item_url} ({content_type})")


def freeze(
    start_from_url: str,
    save_to_path: str,
    thread_pool_size: int = 1,
    http_get_timeout: int = 30,
    skip_extensions: str = None,
    verbose: bool = False,
    dry_run: bool = False,
):
    f = geler.Freezer(
        start_from_url,
        save_to_path,
        thread_pool_size=int(thread_pool_size),
        http_get_timeout=int(http_get_timeout) if int(http_get_timeout) > 0 else None,
        skip_extensions=skip_extensions.split(",") if skip_extensions else None,
        dry_run=dry_run,
    )
    if verbose:
        f.callback_before_save = before_save
    f.freeze()
    if verbose:
        for err in f.http_errors:
            logger.error(f"status {err.get('status_code')} on URL  {err.get('url')}")


def run_cli():
    argh.dispatch_command(freeze)


if __name__ == "__main__":
    run_cli()
