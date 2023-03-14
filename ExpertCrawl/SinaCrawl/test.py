import json
import pymysql
from tqdm import tqdm

code_to_company = {}

with open('Code2Company.json', 'r', encoding='utf-8') as f:
    code_to_company = json.load(f)

# print(code_to_company)
# try:
#     remote_conn = pymysql.Connect(
#         host='120.27.209.14',
#         port=22936,
#         user='yuqi',
#         passwd='yuqi##123',
#         database='Report',
#         cursorclass=pymysql.cursors.DictCursor,
#         charset='utf8'
#     )
# except:
#     print("connect database fail!")

try:
    local_conn = pymysql.connect(
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

local_cursor = local_conn.cursor()

select_sql = '''
    select id, company_stock
    from sina_experts
'''

local_cursor.execute(select_sql)
results = local_cursor.fetchall()

for res in tqdm(results[513:]):

    if res['company_stock'] not in code_to_company:
        print(f'\n股票代码 {res["company_stock"]} 机构名称获取失败' + '=' * 30)
        continue

    code = res['company_stock']
    name = code_to_company[code]

    update_sql = f'''
        update sina_experts
        set company_name = '{name}'
        where id = {res['id']}
    '''

    local_cursor.execute(update_sql)
    local_conn.commit()

local_cursor.close()
# remote_cursor.close()
local_conn.close()
# remote_conn.close()