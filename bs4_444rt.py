from bs4 import BeautifulSoup
import requests
import re
import os
import logging
from multiprocessing import Pool

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

logging.info('program start...')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': "http://www.444rt.com/"
}
SAVE_DIR = 'D:\\tmp\\444rt.com'

categories = {
    'oumeirentiyishu': 'http://www.444rt.com/oumeirentiyishu/',
    'ouzhourentiyishu': 'http://www.444rt.com/ouzhourentiyishu/',
    'eluosirenti': 'http://www.444rt.com/eluosirenti/',
    'oumeitupian': 'http://www.444rt.com/oumeitupian/'
}


def get_girls_in_one_page(page_url='http://www.444rt.com/oumeirentiyishu/'):
    r = requests.get(page_url, headers=headers)
    r.encoding = 'gbk'
    bs = BeautifulSoup(r.text, 'html.parser')

    items = bs.find('div', class_='fzltp').find_all('li')
    for item in items:
        girl_url = item.find('a')['href']
        girl_title = item.find('img')['alt']
        yield girl_url, girl_title


def get_pages_in_one_cat(cat='oumeirentiyishu'):
    cat_url = categories[cat]
    r = requests.get(cat_url, headers=headers)
    r.encoding = 'gbk'
    bs = BeautifulSoup(r.text, 'html.parser')
    item = bs.find('div', class_='pagelist').find_all('a')[-2]
    last_page_url = str(item['href'])
    prefix, total_num_str = re.search('(.*_)(\d+).html', last_page_url).groups()
    total_num = int(total_num_str)

    for i in range(1, total_num + 1):
        if i == 1:
            yield cat_url
        else:
            yield cat_url + prefix + str(i) + '.html'


def get_all_girls():
    for cat in categories:
        for page_url in get_pages_in_one_cat(cat):
            for girl_url, girl_title in get_girls_in_one_page(page_url):
                girl = (girl_url, girl_title, cat)
                yield girl


def get_img_urls_of_one_girl(girl):
    girl_url = 'http://www.444rt.com' + girl[0]
    r = requests.get(girl_url, headers=headers)
    r.encoding = 'gbk'
    bs = BeautifulSoup(r.text, 'html.parser')
    last_page_url = str(bs.find('div', class_='pagelist').find_all('a')[-1]['href'])
    prefix, page_total_num_str = re.match('(.*?)(\d+).html', last_page_url).groups()
    page_total_num = int(page_total_num_str)

    img_urls = []
    ok_count = 0
    for i in range(1, page_total_num + 1):
        if i == 1:
            page_url = girl_url
        else:
            page_url = girl_url + prefix + str(i) + '.html'

        r = requests.get(page_url, headers=headers)
        if r.status_code == 200:
            ok_count += 1
        r.encoding = 'gbk'
        bs = BeautifulSoup(r.text, 'html.parser')
        img_url = bs.find(class_='imgbox').find('img')['src']
        img_urls.append(img_url)
    if ok_count != page_total_num:
        logging.warning('ok_count:{}, page_total_num:{}, url:{}, title:{}.'.format(
                        ok_count, page_total_num, girl[0], girl[1]))
    img_count = ok_count
    return img_urls, img_count


def download_one_girl(girl):
    girl_url, girl_title, cat = girl
    img_dir = os.path.join(SAVE_DIR, cat, girl_title)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    img_urls, img_count = get_img_urls_of_one_girl(girl)

    existed_count = len(os.listdir(img_dir))
    if existed_count:
        if existed_count == img_count:
            logging.info('之前已经完成下载:{0}/{1},  title={2}'.format(
                existed_count, img_count, girl_title))
            return
        else:
            logging.info('上次未完成:{0}/{1},继续下载...  title={2}'.format(
                existed_count, img_count, girl_title))

    for img_url in img_urls:
        pic_name = img_url.split('/')[-1]
        if pic_name in os.listdir(img_dir):
            continue

        r = requests.get(img_url, headers=headers)
        if r.status_code == 200:
            with open(os.path.join(img_dir, pic_name), 'wb') as f:
                f.write(r.content)
        else:
            print(r.status_code)

    logging.info('{}/{} downloaded, title={}'.format(
        len(os.listdir(img_dir)), img_count, girl_title))


def main(girl_list):
    for girl in girl_list:
        download_one_girl(girl)


if __name__ == '__main__':
    logging.info('indexing...')
    girl_list = list(get_all_girls())
    logging.info('一共找到{}个女孩.'.format(len(girl_list)))

    batch = 50
    p_num = len(girl_list) // batch + 1
    pool = Pool(p_num)
    logging.info('即将创建{}个进程进行下载...'.format(p_num))
    for i in range(p_num):
        start = i * batch
        end = (i + 1) * batch
        if (i + 1) * batch > len(girl_list):
            end = len(girl_list)
        pool.apply_async(main, args=(girl_list[start:end],))
    pool.close()
    pool.join()