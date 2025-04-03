from itertools import chain
import urllib.request
import xml.etree.ElementTree as ET
from multiprocessing.pool import ThreadPool
from typing import List, Optional

from tenacity import retry, stop_after_attempt, wait_random_exponential
from langchain.schema import Document
from langchain.document_loaders.base import BaseLoader
from langchain_community.document_loaders import WebBaseLoader

from conf import settings


class SiteLoader(BaseLoader):
    """
    Loads and processes the website pages by parsing a sitemap and retrieving the content of the pages.
    """

    def __init__(
        self,
        site_url: str,
        excluded_urls: Optional[List[str]] = None,
        threads: int = settings.DEFAULT_THREADS,
        limit: int = settings.DEFAULT_LIMIT,
    ) -> None:
        self._site = site_url
        self._sitemap = f"{self._site}/sitemap.xml"
        self._excluded_urls = excluded_urls if excluded_urls is not None else []
        self._threads = threads
        self._limit = limit

    def load(self) -> List[Document]:
        """Load the documentation.

        Returns:
            List[Document]: A list of documents.
        """
        urls = self._get_urls_from_sitemap()
        docs = self._process_urls(urls)
        return docs

    def _get_urls_from_sitemap(self) -> List[str]:
        print('Getting urls from sitemap...')

        sitemap = self._get_parsed_sitemap()

        namespaces = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [
            url.text
            for url in sitemap.findall(".//sitemap:loc", namespaces=namespaces) # looking for loc elements that containes the page url
            if url.text is not None and url.text not in self._excluded_urls
        ]
        urls = urls[: self._limit] if self._limit else urls 

        print(f'URLS founded: {urls}')

        return urls

    def _process_urls(self, urls: List[str]) -> List[Document]:
        print('Processing urls...')
        
        with ThreadPool(self._threads) as pool:
            page_docs = pool.map(self._process_url, urls)
            docs = list(chain.from_iterable(page_docs)) # flatten the list of lists
            return docs

    @retry(
        stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, max=10)
    )
    def _process_url(self, url: str) -> List[Document]:
        print(f'Processing url: {url}')

        web_loader = WebBaseLoader(url)
        page_docs = web_loader.load()
        return page_docs


    def _get_parsed_sitemap(self) -> ET.Element:
        with urllib.request.urlopen(self._sitemap) as response:
            xml = response.read()

        root = ET.fromstring(xml) 
        return root
    