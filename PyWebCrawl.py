# Import libraries
import sys
from urllib.request import urljoin
from bs4 import BeautifulSoup
import requests
from urllib.request import urlparse


# Set for storing urls with same domain
links_intern = set()

# usage message
usage_msg = f"Usage: {sys.argv[0]} http[s]://<domain> <depth_to_crawl>\nDepth: 0-10"

# Set for storing urls with different domain
links_extern = set()


# Method for crawling a url at next level
def level_crawler(input_url):
    temp_urls = set()
    current_url_domain = urlparse(input_url).netloc

    # Creates beautiful soup object to extract html tags
    beautiful_soup_object = BeautifulSoup(requests.get(input_url).content, "lxml")

    # Access all anchor tags from input
    # url page and divide them into internal
    # and external categories
    for anchor in beautiful_soup_object.findAll("a"):
        href = anchor.attrs.get("href")
        if href != "" or href != None:
            href = urljoin(input_url, href)
            href_parsed = urlparse(href)
            href = href_parsed.scheme
            href += "://"
            href += href_parsed.netloc
            href += href_parsed.path
            final_parsed_href = urlparse(href)
            is_valid = bool(final_parsed_href.scheme) and bool(final_parsed_href.netloc)
            if is_valid:
                if "http" not in href:
                    continue
                if current_url_domain not in href and href not in links_extern:
                    # print("Extern - {}".format(href))
                    links_extern.add(href)
                if current_url_domain in href and href not in links_intern:
                    # internal links only
                    print(href)
                    links_intern.add(href)
                    temp_urls.add(href)
    return temp_urls


def start_crawl(input_url, depth):
    if depth == 0:
        print("Intern - {}".format(input_url))
    elif depth == 1:
        level_crawler(input_url)
    else:
        # We have used a BFS approach
        # considering the structure as
        # a tree. It uses a queue based
        # approach to traverse
        # links upto a particular depth.
        queue = []
        queue.append(input_url)
        for j in range(depth):
            for count in range(len(queue)):
                url = queue.pop(0)
                urls = level_crawler(url)
                for i in urls:
                    queue.append(i)
    return list(links_intern)


def test_url(appended_input_url):
    try:
        response = requests.get(appended_input_url)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False
    


def validate_inputs(input_url, depth):
    # make sure that the number of parameters are correct
    if len(sys.argv) != 3:
        print(usage_msg)
        sys.exit(1)
    # make sure that depth that the user input is an integer
    try:
        depth = int(depth)
        if depth > 10:
            print(usage_msg)
            sys.exit(1)
    except ValueError as e:
        print(usage_msg)
        print("Depth must be an integer")
        sys.exit(1)
    # make sure that the url that is provided starts with http:// or https://
    if not input_url.startswith("http://") or not input_url.startswith("https://"):
        # means that input_url doesnt starts with http or https
        # we append http and https and check if it exist
        # have a flag to check http or https
        test_flag = 0
        if test_url(f"http://{input_url}"):
            test_flag += 1
        if test_url(f"http://{input_url}"):
            test_flag += 2
        # now we check whats the value
        # 0, means none works AKA invalid link provided
        if test_flag == 0:
            print(usage_msg)
            print("Please provide a value url")
            sys.exit(1)
        # 1, means that only http works
        if test_flag == 1:
            input_url = f"http://{input_url}"
        # 2, means that only https works
        if test_flag == 2:
            input_url = f"https://{input_url}"
        # 3, means both http and https works, we just choose http
        if test_flag == 3:
            input_url = f"http://{input_url}"
    return input_url, depth


def main():
    input_url = sys.argv[1]
    depth = sys.argv[2]

    input_url, depth = validate_inputs(input_url, depth)

    print(start_crawl(input_url, depth))


if __name__ == "__main__":
    main()

