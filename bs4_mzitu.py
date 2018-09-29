from bs4 import BeautifulSoup
import requests
import re
import os
import logging
from multiprocessing import Pool


logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

logging.info('program start...')

BASE_URL = 'http://www.mzitu.com'

SAVE_DIR = 'D:\\tmp\\mzitu.com'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': BASE_URL
}

requests.adapters.DEFAULT_RETRIES = 5


def get_all_pages():
    r = requests.get(BASE_URL, headers=headers)
    bs = BeautifulSoup(r.content, 'html.parser')
    last_page_url = bs.find(class_='nav-links').find_all('a')[-2]['href']
    total_page_num_str = last_page_url.strip('/').split('/')[-1]
    total_page_num = int(total_page_num_str)

    for i in range(1, total_page_num + 1):
        if i == 1:
            yield BASE_URL
        else:
            yield last_page_url.replace(total_page_num_str, str(i))


def get_girls_in_one_page(page_url=BASE_URL):
    r = requests.get(page_url, headers=headers)
    bs = BeautifulSoup(r.content, 'html.parser')
    items = bs.find(id='pins').find_all('li')
    for item in items:
        girl_url = item.find('a')['href']
        girl_title = item.find('img')['alt']
        yield girl_url, girl_title


def get_all_girls():
    for page_url in get_all_pages():
        for girl in get_girls_in_one_page(page_url):
            yield girl


def get_img_urls_of_one_girl(girl_url='http://www.mzitu.com/149728'):
    r = requests.get(girl_url, headers=headers)
    bs = BeautifulSoup(r.content, 'html.parser')
    total_page_num = int(bs.find(class_='pagenavi').find_all('a')[-2].span.string)

    img_urls = []
    for i in range(1, total_page_num + 1):
        if i == 1:
            page_url = girl_url
        else:
            page_url = girl_url + '/' + str(i)
        r = requests.get(page_url, headers=headers)
        bs = BeautifulSoup(r.content, 'html.parser')
        img_url = bs.find(class_='main-image').find('img')['src']
        img_urls.append(img_url)
    return img_urls


def download_one_girl(girl):
    girl_url, girl_title = girl
    img_urls = get_img_urls_of_one_girl(girl_url)

    total_num = len(img_urls)
    logging.debug('找到{}张照片.{}'.format(total_num, girl_title))

    girl_title = girl_title.replace('?', '')
    girl_title = girl_title.strip()
    img_dir = os.path.join(SAVE_DIR, girl_title)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    existed_count = len(os.listdir(img_dir))
    if existed_count:
        if existed_count >= total_num:
            logging.info('之前已经完成下载:{0}/{1}, title={2}'.format(
                existed_count, total_num, girl_title))
            return
        else:
            logging.info('上次未完成:{0}/{1},继续下载...  title={2}'.format(
                existed_count, total_num, girl_title))

    for img_url in img_urls:
        pic_name = img_url.split('/')[-1]
        if pic_name in os.listdir(img_dir):
            continue

        r = requests.get(img_url, headers=headers)
        if r.status_code == 200:
            with open(os.path.join(img_dir, pic_name), 'wb') as f:
                f.write(r.content)
        else:
            logging.warning(str(r.status_code) + ' ' + img_url)

    logging.info('{}/{} downloaded, title={}'.format(
        len(os.listdir(img_dir)), total_num, girl_title))


def main(page_list, pid):
    def go():
        try:
            logging.info('pid:{} start.'.format(pid))
            for page_url in page_list:
                for girl in get_girls_in_one_page(page_url):
                    download_one_girl(girl)
        except Exception as e:
            logging.info(e)
    go()


if __name__ == '__main__':
    logging.info('indexing...')
    batch = 5
    page_list = list(get_all_pages())
    p_num = len(page_list) // batch
    logging.info('一种找到{}个页面.'.format(len(page_list)))
    logging.info('即将创建{}个进程进行下载...'.format(p_num))
    pool = Pool(p_num)
    for i in range(p_num):
        start = i * batch
        end = (i + 1) * batch
        if end >= len(page_list):
            end = len(page_list)
        pool.apply_async(main, args=(page_list[start:end], i))
    pool.close()
    pool.join()









