import sys
from pathlib import Path
import pandas as pd
import pymysql
from tqdm import tqdm
from Levenshtein import ratio
from utils.InstitudeSimplify import get_short_name
import json
import os
import requests
import time
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)


current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))


def texsmart_query(q1, q2, q_alg):

    obj = {
        'text_pair_list': [{'str1': q1, 'str2': q2}],
        'options': {'alg': q_alg},
        'echo_data': {'id': 123}
    }

    reg_str = json.dumps(obj).encode()
    url = "https://texsmart.qq.com/api/match_text"
    try:
        r = requests.post(url, data=reg_str).json()
        ret_code = r["header"]["ret_code"]
    except Exception as e:
        print(f"texsmart匹配出错: {str(e)}")
        return 0.0
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
    except Exception as e:
        print('error:'+str(e))
        print("connect database fail!")

    local_cursor = conn.cursor()
    write_path = BASE_DIR + f'/experts_info_{current_date}.json'
    sina_experts_result_list = []

    for expert in experts_list:
        name, institute = expert['inventor_name'], expert['full_name']
        # print('\n',name, institute)
        sql = f'''
            select * 
            from sina_experts
            where name = '{name}'
        '''

        local_cursor.execute(sql)
        results = local_cursor.fetchall()
        if results == ():
            print('\n' + '=' * 30 + f'\n专家 {name}---{institute} 新浪源匹配失败\n' + '=' * 30)
            continue

        # 当前专家姓名匹配的数据中找到机构名匹配的数据
        for res in results:
            if res['company_name'] == '':
                continue
            sim = 0.0
            try:
                sim1, sim2 = texsmart_query(institute, res['company_name'], 'esim'), texsmart_query(institute, res['company_name'], 'linkage')
                sim = sim1 * 0.5 + sim2 * 0.5
                print(institute, res['company_name'], sim)
            except Exception as e:
                print(f'Texsmart请求失败:\n{e}')
            cv_info = res['cv']

            if sim > 0.5:
                expert['position'] = res['position']
                expert['nationality'] = res['nationality']
                expert['cv'] = res['cv']
                expert['sina_url'] = res['url']
                expert['edu_background'] = res['edu_background']
                sina_experts_result_list.append((expert, sim))
            sina_experts_result_list.sort(key=lambda x: x[1], reverse=True)
    for expert in sina_experts_result_list[:1]:
        data_in = json.dumps(expert, ensure_ascii=False)
        with open(write_path, 'a', encoding='utf-8') as f:
            f.write(data_in + '\n')

    local_cursor.close()
    conn.close()


if __name__ == '__main__':
    # sina_info_get_run()
    pass




