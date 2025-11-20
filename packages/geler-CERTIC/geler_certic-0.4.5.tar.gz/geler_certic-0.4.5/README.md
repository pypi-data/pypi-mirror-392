# Geler

Help convert dynamic websites to static ones.

## Install

    pip install geler-CERTIC

## Usage

As a library in your own program:

    import geler
    freezer = geler.Freezer(
        "https://acme.tld/",
        "/save/to/path/",
        thread_pool_size=10,
        http_get_timeout=30,
        skip_extensions=[".mp4", ".mp3"],
    ).freeze()

    for err in result.http_errors:
        print(f'{err.get("status_code")}: {err.get("url")}')

As a CLI tool:

    $> geler --help
    usage: geler [-h] [-t THREAD_POOL_SIZE] [--http-get-timeout HTTP_GET_TIMEOUT] [-s SKIP_EXTENSIONS] [-v] start-from-url save-to-path
    
    positional arguments:
      start-from-url        -
      save-to-path          -
    
    optional arguments:
      -h, --help            show this help message and exit
      -t THREAD_POOL_SIZE, --thread-pool-size THREAD_POOL_SIZE
                            1
      --http-get-timeout HTTP_GET_TIMEOUT
                            30
      -s SKIP_EXTENSIONS, --skip-extensions SKIP_EXTENSIONS
                            -
      -v, --verbose         False


Thread pool size (`--thread-pool-size`) defaults to 1. Increase the number to have multiple downloads in parallel.

HTTP get timeout (`--http-get-timeout`) default to 30s. This includes the time needed to download the file. Increase the number to increase the timeout, or set it to 0 for no timeout.

List of skipped  (`--skip-extensions`) is a comma-separated list of extensions that won't be downloaded.

Verbose mode (`--verbose`) will show downloaded URLs and HTTP errors.

Complete example:

    geler --http-get-timeout 30 --thread-pool-size 10 --skip-extension ".mp4,.zip" https://acme.tld/ /path/to/local/dir

## Why ?

For [MaX](https://git.unicaen.fr/pdn-certic/MaX) and associated tools, 
we needed a lightweight, portable, pure Python solution to convert 
small dynamic websites to static ones.

## Alternatives

This tool has a narrow scope, on purpose. Please turn to these solutions if you need more:

- [wget](https://www.gnu.org/software/wget/)
- [pywebcopy](https://pypi.org/project/pywebcopy/)
- [HTTrack](https://www.httrack.com)

## Known Limitations

- only works with HTTP GET
- does not submit forms (even with GET method)
- only considers URLs in `src` or `href` attributes
- only considers URLs with `http` or `https` schemes
- only downloads what is in the same [netloc](https://docs.python.org/3/library/urllib.parse.html) (same domain, same port) as the start URL
- only patches URLs in `*.html` files and `*.css` files, not `*.js` files (watch out for modules import)
- does not throttle requests
- does not respect `robots.txt` or `<meta name="robots" content="noindex">` or any other robot directives.