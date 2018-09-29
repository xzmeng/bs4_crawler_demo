from bs4 import BeautifulSoup
import requests
import re
import os
import logging
from multiprocessing import Pool

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

logging.info('program start...')

BASE_URL = 'http://www.mmjpg.com'

SAVE_DIR = 'D:\\tmp\\mmjpg.com'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': 'http://www.mm131.com'
}


def get_all_pages():
    r = requests.get(BASE_URL, headers=headers)
    bs = BeautifulSoup(r.content, 'html.parser')
    last_page_rel_url = bs.find('a', class_='last')['href']
    prefix, total_page_num_str = re.search('(.*/)(\d+)', last_page_rel_url).groups()
    total_page_num = int(total_page_num_str)
    for i in range(1, total_page_num):
        if i == 1:
            yield BASE_URL
        else:
            rel_url = prefix + str(i)
            yield BASE_URL + rel_url


def get_girls_in_one_page(page_url=BASE_URL):
    r = requests.get(page_url, headers=headers)
    bs = BeautifulSoup(r.content, 'html.parser')
    items = bs.find(class_='pic').find_all('li')
    for item in items:
        item = item.find(class_='title').a
        girl_url = item['href']
        girl_title = str(item.string)
        yield girl_url, girl_title


def get_img_urls_of_one_girl(girl):
    girl_url, girl_title = girl
    r = requests.get(girl_url, headers=headers)
    bs = BeautifulSoup(r.content, 'html.parser')
    last_rel_url = bs.find(id='page').find_all('a')[-2]['href']
    total_num = int(last_rel_url.split('/')[-1])

    img_urls = []
    for i in range(1, total_num + 1):
        if i == 1:
            pass
        else:
            r = requests.get(girl_url + '/' + str(i), headers=headers)
            bs = BeautifulSoup(r.content, 'html.parser')
        img_url = bs.find(id='content').img['src']
        img_urls.append(img_url)
    return img_urls


def download_one_girl(girl):
    girl_title = girl[1]
    img_urls = get_img_urls_of_one_girl(girl)
    total_num = len(img_urls)
    logging.debug('找到{}张照片.{}'.format(total_num, girl_title))

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


def main(page_list):
    for page_url in page_list:
        for girl in get_girls_in_one_page(page_url):
            try:
                download_one_girl(girl)
            except Exception as e:
                logging.error(e)


if __name__ == '__main__':
    batch = 3
    page_list = list(get_all_pages())
    p_num = len(page_list) // batch

    logging.info('即将创建{}个进程进行下载...'.format(p_num))
    pool = Pool(p_num)
    for i in range(p_num):
        start = i * batch
        end = (i + 1) * batch
        if end >= len(page_list):
            end = len(page_list)
        pool.apply_async(main, args=(page_list[start:end],))
    pool.close()
    pool.join()






