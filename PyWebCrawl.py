import sys
import requests
import requests.exceptions
from bs4 import BeautifulSoup
from collections import deque
from time import sleep
from urllib.parse import urlsplit
from urllib.parse import urlparse


class PyWebCrawl:
    def __init__(self, start_url):

        # init name of crawler
        self.name = "webapp_crawler"

        # init counter from 0
        self.counter = 0

        # init url from param
        self.url = start_url

        # a queue of urls to be crawled next
        self.new_urls = deque([self.url])

        # a set of urls that we have already processed
        self.processed_urls = set()

        # a set of domains inside the target website
        self.local_urls = set()

        # a set of domains outside the target website
        self.foreign_urls = set()

        # a set of broken urls
        self.broken_urls = set()

        # a set of visited url
        self.visited_urls = set()
        
        # add list of blacklisted pages or words to avoid spidering them
        self.lst_blacklist = ['..', 'mailto']

    def crawl(self):
        # process urls one by one until we exhaust the queue
        while self.new_urls:
            # move url from the queue to processed url set
            url = self.new_urls.popleft()
            self.processed_urls.add(url)
            # print the current url
            # print(f"Processing {self.url}")

            try:
                response = requests.get(url)
            except (
                requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError,
                requests.exceptions.InvalidURL,
                requests.exceptions.InvalidSchema,
            ):
                # add broken urls to it’s own set, then continue
                self.broken_urls.add(url)
                continue
            # extract base url to resolve relative links
            parts = urlsplit(url)
            base = "{0.netloc}".format(parts)
            strip_base = base.replace("www.", "")
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[: url.rfind("/") + 1] if "/" in parts.path else url

            # create a beutiful soup for the html document
            soup = BeautifulSoup(response.text, "lxml")

            for link in soup.find_all("a"):
                # bool contains blacklist
                bool_contains_blacklist = False
            
                # extract link url from the anchor
                anchor = link.attrs["href"] if "href" in link.attrs else ""
                
                for blacklisted in self.lst_blacklist:
                    if blacklisted in anchor:
                        bool_contains_blacklist = True
                if bool_contains_blacklist:
                    continue
                if anchor.startswith("/"):
                    local_link = base_url + anchor
                    self.local_urls.add(local_link)
                elif strip_base in anchor:
                    self.local_urls.add(anchor)
                elif not anchor.startswith("http"):
                    local_link = path + anchor
                    self.local_urls.add(local_link)
                else:
                    self.foreign_urls.add(anchor)
                for i in self.local_urls:
                    if not i in self.new_urls and not i in self.processed_urls:
                        self.new_urls.append(i)
                        print(i)
        # for processed_url in self.processed_urls:
        # print(processed_url)
        return self.processed_urls


def main():
    # Ensure that the program is supplied a url to start crawling
    if len(sys.argv) != 2:
        print("Please provide a url to crawl")
        sys.exit()
    start_url = sys.argv[1]  # can use http://books.toscrape.com/ for testing
    spider = PyWebCrawl(start_url)
    res = spider.crawl()
    print(res)
    print(len(res))


if __name__ == "__main__":
    main()
