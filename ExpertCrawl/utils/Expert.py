# 数据库连接
from utils.conn_mysql import conn_ali_mysql
# 机构名简化
from utils.InstitudeSimplify import get_short_name

import requests
from tqdm import tqdm

class Expert():
    """专家类
    包含专家的获取、入库等操作
    """
    def __init__(self) -> None:
        self.db = "suwen_data"
    
    # 获取企业专家数据列表
    # def get_expert_list(self) -> list:
    #     api = "http://120.27.209.14:22922/news/expert_list/"
    #     res_list = requests.get(api).json()
    #     return res_list

    # TODO 获取企业专家数据列表
    def get_expert_list(self) -> list:
        # sql = "SELECT id, name, scholar_institute from scholar where scholar_institute not like '%学院%' and scholar_institute not like '%大学%' and scholar_institute not like '%研究院%' limit 100 offset 30"
        # res_list, _ = conn_ali_mysql(sql, database=self.db)
        api = "http://120.27.209.14:22922/news/expert_list"
        res_list = requests.get(api).json()
        expert_list = res_list["data"][:20]
        # print(expert_list)
        # expert_list = [{"id":res[0], "name":res[1], "institute":res[2]} for res in res_list]

        print('=' * 15 + '专家机构简称名开始获取' + '=' * 15)

        for expert in tqdm(expert_list):
            simply_sql = f'''
                SELECT short_name
                FROM company
                WHERE full_name = '{expert["scholar_institute"]}'
                LiMIT 1
            '''

            result, _ = conn_ali_mysql(simply_sql)
            simply_institute = ''
            if result == ():
                simply_institute = get_short_name(expert["scholar_institute"])
            else:
                simply_institute = result[0][0]
            # 可能会出现简化为空的情况
            if simply_institute == '':
                simply_institute = expert["scholar_institute"]

            expert["simply_institute"] = simply_institute

        return expert_list
    
    # 企业专家数据入库
    def insert_expert(self) -> None:
        sql = "insert into scholar set"
