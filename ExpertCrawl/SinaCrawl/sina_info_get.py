import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
import pandas as pd
import pymysql
from tqdm import tqdm
from Levenshtein import ratio
from utils.InstitudeSimplify import get_short_name
import json
import os
import requests
import time


current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

def texsmart_query(q1, q2, q_alg):

    obj = {
        'text_pair_list': [{'str1': q1, 'str2': q2}],
        'options': {'alg': q_alg},
        'echo_data': {'id': 123}
    }

    reg_str = json.dumps(obj).encode()
    url = "https://texsmart.qq.com/api/match_text"
    r = requests.post(url, data=reg_str).json()
    ret_code = r["header"]["ret_code"]
    while ret_code != "succ":
        r = requests.post(url, data=reg_str).json()
        ret_code = r["header"]["ret_code"]

    return r['res_list'][0]['score']


def sina_info_get_run(experts_list):

    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='yang8302',
            database='expertcrawl',
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8')
    except:
        print("connect database fail!")

    local_cursor = conn.cursor()

    # data_path = base_path + '/experts_input.json'
    write_path = BASE_DIR + f'/experts_info_{current_date}.json'
    #
    # with open(data_path, 'r', encoding='utf-8') as f:
    #     for line in f.readlines():
    #         data_out = json.loads(line)
    #         experts_list.append(data_out)

    # print(experts_list[:10])
    sina_experts_result_list = []

    for expert in experts_list:
        name, institute = expert['name'], expert['scholar_institute']
        # print('\n',name, institute)
        sql = f'''
            select * 
            from sina_experts
            where name = '{name}'
        '''

        local_cursor.execute(sql)
        results = local_cursor.fetchall()
        if results == ():
            print(f'\n专家 {name}---{institute}匹配失败\n' + '=' * 30)
            continue

        # 当前专家姓名匹配的数据中找到机构名匹配的数据
        for res in results:

            if res['company_name'] == '':
                continue

            try:
                short_institute, short_company = get_short_name(institute), get_short_name(res['company_name'])
            except Exception as e:
                print(f'\n简称处理错误: {e}')
                continue

            if short_institute == '' or short_company == '':
                continue
            sim1, sim2 = texsmart_query(short_institute, short_company, 'esim'), texsmart_query(short_institute, short_company, 'linkage')
            sim = sim1 * 0.5 + sim2 * 0.5
            cv_info = res['cv']

            if sim > 0.45 or short_institute in cv_info:

                # expert['gender'] = res['gender']
                # expert['company_stock'] = res['company_stock']
                # expert['company_name'] = res['company_name']
                expert['occupation'] = res['position']
                # expert['edu_background'] = res['edu_background']
                expert['nationality'] = res['nationality']
                expert['scholar_brief_info'] = res['cv']
                expert['sina_url'] = res['url']
                expert['edu_level'] = res['edu_background']
                print(expert)
                print('\n' + '=' * 30)
                sina_experts_result_list.append(expert)
    # print(sina_experts_result_list)
    for expert in sina_experts_result_list:
        # print(expert)
        data_in = json.dumps(expert, ensure_ascii=False)
        with open(write_path, 'a', encoding='utf-8') as f:
            f.write(data_in)
            f.write('\n')

    local_cursor.close()
    conn.close()

if __name__ == '__main__':

    # sina_info_get_run()
    pass




