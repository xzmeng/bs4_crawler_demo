from bs4 import BeautifulSoup
import requests
import re
import os
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

logging.info('program start...')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': "http://www.mm131.com/"
}
# SAVE_DIR = 'D:\\tmp\\mm131_bs4'
SAVE_DIR = 'D:\\tmp\\mm131_bs4_thread'
IMG_PREFIX = 'http://img1.mm131.me/pic/'
categories = {
        'xinggan': 'http://www.mm131.com/xinggan/',
        'qingchun': 'http://www.mm131.com/xinggan/',
        'xiaohua': 'http://www.mm131.com/xiaohua/',
        'chemo': 'http://www.mm131.com/chemo/',
        'qipao': 'http://www.mm131.com/qipao/',
        'mingxing': 'http://www.mm131.com/mingxing/',
}


def get_pages_in_one_category(cat='qipao'):
    cat_url = categories[cat]
    r = requests.get(cat_url, headers=headers)
    r.encoding = 'gbk'
    bs = BeautifulSoup(r.text, 'html.parser')
    last_page = bs.find_all('a', class_='page-en')[-1]

    result = re.search('(.*_)(\d+).html', last_page['href'])  # 搜索一个类别中不同页面的前缀和总页数
    prefix = result.group(1)
    total_page_num = int(result.group(2))

    for i in range(1, total_page_num + 1):
        if i == 1:
            yield cat_url
        else:
            yield cat_url + prefix + str(i) + '.html'


def get_girls_in_one_page(page_url='http://www.mm131.com/qipao/'):
    r = requests.get(page_url, headers=headers)
    r.encoding = 'gbk'
    bs = BeautifulSoup(r.text, 'html.parser')
    items = bs.find('dl', class_='list-left').find_all('dd', class_=None)
    for item in items:
        girl_url = item.a['href']
        girl_title = str(item.a.img['alt'])
        yield girl_url, girl_title


def get_girls_in_one_category(cat='qipao'):
    for page_url in get_pages_in_one_category(cat):
        for girl_url, girl_title in get_girls_in_one_page(page_url):
            yield girl_url, girl_title, cat


######################################
# 返回(url, title, category)
def get_girls_in_all_categories():
    for cat in categories:
        for girl in get_girls_in_one_category(cat):
            yield girl
######################################


def get_img_urls_of_one_girl(girl_url='http://www.mm131.com/qipao/2288.html'):
    r = requests.get(girl_url, headers=headers)
    r.encoding = 'gbk'
    page_count = int(re.search('共(\d+)页', r.text).group(1))
    img_count = page_count
    girl_id = re.search('(\d+).html', girl_url).group(1)
    prefix = IMG_PREFIX + girl_id + '/'
    img_urls = []
    for i in range(1, img_count + 1):
        img_url = prefix + str(i) + '.jpg'
        img_urls.append(img_url)
    return img_urls, img_count, girl_id


def download_one_girl(girl):
    girl_url, girl_title, cat = girl
    img_dir = os.path.join(SAVE_DIR, cat, girl_title)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    img_urls, img_count, girl_id = get_img_urls_of_one_girl(girl_url)

    existed_count = len(os.listdir(img_dir))
    if existed_count:
        if existed_count == img_count:
            logging.info('之前已经完成下载:{0}/{1}, girl_id={2}, title={3}'.format(
                existed_count, img_count, girl_id, girl_title))
            return
        else:
            logging.info('上次未完成:{0}/{1},继续下载... girl_id={2}, title={3}'.format(
                existed_count, img_count, girl_id, girl_title))

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

    logging.info('{}/{} downloaded, girl_id={}, title={}'.format(
        len(os.listdir(img_dir)), img_count, girl_id, girl_title))


def download_all():
    for girl in get_girls_in_all_categories():
        try:
            download_one_girl(girl)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    download_all()









