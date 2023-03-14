import json
import pymysql
from tqdm import tqdm
import time
import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

def sina_to_database_run():
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

    expert_list = []

    data_path = BASE_DIR + f'/experts_info_{current_date}.json'

    with open(data_path,'r',encoding='utf-8') as f:
        for line in f.readlines():
            data_out = json.loads(line)
            expert_list.append(data_out)

    for index, expert in enumerate(tqdm(expert_list)):

        name, stockid, position, gender = expert['name'], expert['com_stock'], expert['position'], expert['gender']
        edu, nationality, cv, url = expert['edu_background'], expert['nationality'], expert['cv'], expert['url']

        sql = f'''
            insert into sina_experts (name, gender, company_stock, position, edu_background, nationality, cv, url)
            values ('{name}', '{gender}', '{stockid}', '{position}', '{edu}', '{nationality}', '{cv}', '{url}')
        '''

        local_cursor.execute(sql)
        conn.commit()

    local_cursor.close()
    conn.close()
