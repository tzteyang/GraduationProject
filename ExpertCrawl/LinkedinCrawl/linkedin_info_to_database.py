import json
import pymysql
import os
from tqdm import tqdm
import time
import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

def linkedin_to_database_run():
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='yang8302',
            database='expertcrawl',
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8'
        )
    except:
        print("connect database fail!")

    local_cursor = conn.cursor()

    experts_list = []

    data_path = BASE_DIR + f'/experts_info_{current_date}.json'

    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            data_out = json.loads(line)
            experts_list.append(data_out)

    # print(experts_list)
    for expert in tqdm(experts_list):

        select_sql = f'''
            select count(*)
            from experts
            where id = {expert['id']}
        '''

        local_cursor.execute(select_sql)
        res = local_cursor.fetchone()
        cnt = res['count(*)']

        id, name, institute, simply_institute, position = expert["id"], expert["name"], expert["institute"], expert["simply_institute"], expert["position"]
        work_experience, edu_experience, url = expert["work_experience"], expert["edu_experience"], expert["url"]
        # 字典写入sql语句是一定要转义'
        work_experience = str(work_experience).replace("\'", "\\\'")
        edu_experience = str(edu_experience).replace("\'", "\\\'")

        if cnt == 0:
            insert_sql = f'''
                insert into experts (id, name, institute, simply_institute, Lposition, work_experience, edu_experience, linkedin_url)
                values ({id}, '{name}', '{institute}', '{simply_institute}', '{position}', '{work_experience}', '{edu_experience}', '{url}')
            '''
            # print(insert_sql)
            local_cursor.execute(insert_sql)
            conn.commit()
        else:
            update_sql = f'''
                update experts
                set Lposition = '{position}', work_experience = '{work_experience}', edu_experience = '{edu_experience}', linkedin_url = '{url}'
                where id = {expert["id"]}
            '''
            # print(update_sql)
            local_cursor.execute(update_sql)
            conn.commit()

    local_cursor.close()
    conn.close()