from bs4_mm131 import *
from multiprocessing import Pool


def main(process_girl_list):
    for girl in process_girl_list:
        try:
            download_one_girl(girl)
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':  # 请不要
    logging.info('indexing...')
    girl_list = list(get_girls_in_all_categories())
    logging.info('一共找到{}个女孩.'.format(len(girl_list)))

    batch = 200
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

