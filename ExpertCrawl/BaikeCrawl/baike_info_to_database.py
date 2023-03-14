import json
import pymysql
import os
from tqdm import tqdm
import jsonlines
import time

current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

def baike_to_database_run():
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

    # experts_list = []

    base_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
    print(base_path)
    data_path = base_path + f'/ExpertCrawl/BaikeCrawl/output/baike_info_{current_date}.jsonl'

    experts_list = list(jsonlines.open(data_path))

    # print(experts_list)
    for expert in tqdm(experts_list):

        if 'data' not in expert:
            continue

        select_sql = f'''
            select count(*)
            from experts
            where id = {expert['id']}
        '''

        local_cursor.execute(select_sql)
        res = local_cursor.fetchone()
        cnt = res['count(*)']

        id, name, institute, simply_institute = expert["id"], expert["name"], expert["institute"], expert["simply_institute"]
        data = expert["data"]
        # 字典写入sql语句是一定要转义'
        # work_experience = str(work_experience).replace("\'", "\\\'")
        # edu_experience = str(edu_experience).replace("\'", "\\\'")
        data = str(data).replace("\'", "\\\'")

        if cnt == 0:
            insert_sql = f'''
                insert into experts 
                (id, name, institute, simply_institute, baike_json)
                values 
                ({id}, '{name}', '{institute}', '{simply_institute}', '{data}')
            '''
            # print(insert_sql)
            local_cursor.execute(insert_sql)
            conn.commit()
        else:
            update_sql = f'''
                update experts
                set baike_json = '{data}'
                where id = {id}
            '''
            # print(update_sql)
            local_cursor.execute(update_sql)
            conn.commit()

    local_cursor.close()
    conn.close()