"""WebDriver compatibility utilities"""

from .chrome import get_chrome_version, get_chromedriver_version, download_chromedriver
from .edge import get_edge_version, get_msedgedriver_version, download_msedgedriver
from .firefox import get_firefox_version, get_geckodriver_version, download_geckodriver

__all__ = [
    "get_chrome_version", "get_chromedriver_version", "download_chromedriver",
    "get_edge_version", "get_msedgedriver_version", "download_msedgedriver",
    "get_firefox_version", "get_geckodriver_version", "download_geckodriver",
]
