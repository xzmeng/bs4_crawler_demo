from bs4 import BeautifulSoup
import requests
START_URL = 'https://www.23us.so/top/allvisit_1.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': "https://www.23us.so/"
}


class Fiction:
    def __init__(self):
        self.name = ''
        self.author = ''
        self.words = 0


def get_bs(url):
    r = requests.get(url, headers=headers)
    bs = BeautifulSoup(r.content, 'html.parser')
    return bs


def get_all_pages():
    bs = get_bs(START_URL)
    last_page = bs.find('a', class_='last')
    last_page_url = last_page['href']
    total_page_num = int(last_page.string)
    for i in range(1, total_page_num+1):
        yield last_page_url.replace(last_page.string, str(i))


def get_fictions_in_one_page(page_url=START_URL):
    bs = get_bs(page_url)
    items = bs.find('table').find_all('tr')[1:]
    print(items)


get_fictions_in_one_page()