# 导入信息爬取函数
from utils.selenium_tool import selenium_entity
from LinkedinCrawl.linkedin_url_crawl import linkedin_url_get_run
from LinkedinCrawl.linkedin_info_crawl import Cookies_add, Cookies_get
from LinkedinCrawl.linkedin_info_crawl import linkedin_info_get_run
from SinaCrawl.sina_info_get import sina_info_get_run
from CnkiCrawl.cnki_url_crawl import cnki_url_get_run
from CnkiCrawl.cnki_info_crawl import cnki_info_get_run, login_list_get, user_login, user_exit
from BaikeCrawl.baike_info_crawl import baike_info_get_run
from ExpertGraph.utils.db_conn import local_db

import jsonlines
import time
from tqdm import tqdm
import json


class ExpertCrawlRun:

    def __init__(self, s_file):
        self.data_list = []
        db = local_db(database='report', datasource='local')
        sql = """
            select inventor_id, inventor_name, full_name, short_name
            from inventors_company
            order by T_index desc 
            limit 10
            offset 0
        """
        print('专家列表获取中......')
        self.data_list = db.query_all(sql)
        print('专家列表获取完毕!!!')
        db.db_close()
        self.save_file = s_file
    
    def fetch_expert_info(self):
        # 获取专家列表
        expert_list = self.data_list
        # 计时函数
        start = time.perf_counter()
        # 信息源耗时函数
        linkedin_cost, cnki_cost, baike_cost = 0, 0, 0

        # 创建知网学者库窗口
        cnki_window = selenium_entity(url='https://expert.cnki.net/', headless=True)
        cnki_window.browser_run()
        login_list = login_list_get()
        user_login(cnki_window, login_list[1]["account"], login_list[1]["password"])

        for index, expert in enumerate(tqdm(expert_list)):

            print(f'\n专家\n {expert}\n 信息开始获取')
            print('@' * 30)

            linkedin_window = selenium_entity(url='https://cn.bing.com/', headless=True)
            linkedin_window.browser_run()

            linkedin_start = time.perf_counter()
            # 领英主页地址
            linkedin_url_get_run(linkedin_window, [expert])
            # 领英主页信息
            linkedin_info_get_run(linkedin_window, [expert])
            linkedin_window.browser_close()
            linkedin_end = time.perf_counter()
            linkedin_cost += linkedin_end - linkedin_start
            #
            cnki_start = time.perf_counter()
            # 知网学者库主页地址
            cnki_url_get_run([expert])
            # 知网学者库主页信息
            cnki_info_get_run(cnki_window, [expert], index)
            cnki_end = time.perf_counter()
            cnki_cost += cnki_end - cnki_start
            #
            # 新浪源数据库匹配
            sina_info_get_run([expert])

            baike_start = time.perf_counter()
            # 百度百科爬取
            baike_info_get_run([expert])
            baike_end = time.perf_counter()
            baike_cost += baike_end - baike_start

            print(f'\n专家\n {expert}\n 信息获取完成')
            print('@' * 30)

            self.data_write(expert)

        # linkedin_window.browser_close()
        cnki_window.browser_close()

        # 结束运行
        end = time.perf_counter()

        cost = end - start
        h, m = cost // 3600, (cost % 3600) // 60
        print(f'程序运行总耗时: {h}h{m}min')

        lh, lm, ls = linkedin_cost // 3600, (linkedin_cost % 3600) // 60, linkedin_cost % 60
        print(f'领英运行耗时: {lh}h{lm}min{ls}s')

        ch, cm, cs = cnki_cost // 3600, (cnki_cost % 3600) // 60, cnki_cost % 60
        print(f'知网学者库运行耗时: {ch}h{cm}min{cs}s')

        bh, bm, bs = baike_cost // 3600, (baike_cost % 3600) // 60, baike_cost % 60
        print(f'百科运行耗时: {bh}h{bm}min{bs}s')

    def data_write(self, data: dict):
        # data_in = json.dumps(data, ensure_ascii=False)
        with jsonlines.open(self.save_file, 'a') as f:
            f.write(data)


if __name__ == '__main__':
    pass
