from bs4_mm131 import *
from concurrent.futures import ThreadPoolExecutor


def main(thread_girl_list):
    for girl in thread_girl_list:
        try:
            download_one_girl(girl)
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':  # 请不要
    logging.info('indexing...')
    girl_list = list(get_girls_in_all_categories())
    logging.info('一共找到{}个女孩.'.format(len(girl_list)))

    batch = 200
    t_num = len(girl_list) // batch + 1
    executor = ThreadPoolExecutor(max_workers=t_num)

    for i in range(t_num):
        start = i * batch
        end = (i + 1) * batch
        if (i + 1) * batch > len(girl_list):
            end = len(girl_list)
        executor.submit(main, girl_list[start:end])

    print('ok')









