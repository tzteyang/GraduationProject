import json
import sys
from pymysql.converters import escape_string
from ExpertGraph.utils.db_conn import local_db
from pathlib import Path
from tqdm import tqdm
# 当前项目路径获取
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
DATA_DIR = BASE_DIR + '/SummaryData/output/all_experts_info_<date>.json'

# 构造对象key与数据库column对应关系字典
crawlKey2col = {
    'inventor_id': 'inventor_id',
    'inventor_name': 'name',
    'full_name': 'institute',
    'short_name': 'simply_institute',
    'linkedin_position': 'position',
    'work_experience': 'work_experience',
    'edu_experience': 'edu_experience',
    'edu_background': 'edu_background',
    'linkedin_url': 'linkedin_url',
    'research_field': 'research_field',
    'domain': 'domain',
    'download': 'download',
    'refer': 'refer',
    'cnki_url': 'cnki_url',
    'nationality': 'nationality',
    'cv': 'cv',
    'sina_url': 'sina_url',
    'baike_info': 'baike_info',
    'achievements': 'achievements',
    'expert_experience': 'expert_experience',
    'awards': 'awards',
    'graduate_university': 'graduate_university',
}


def read_file(file_date):
    experts_list = []

    with open(DATA_DIR.replace('<date>', file_date), 'r', encoding='utf-8') as f:
        for line in f.readlines():
            experts_list.append(json.loads(line))
    return experts_list


def insert_sql_gen(expert):
    # 预处理
    if ('position' in expert) and (expert['position'] != '' and '公司' in expert['position']):
        expert['position'] = expert['linkedin_position'] if 'linkedin_position' in expert else ''
    if (not 'graduate_university' in expert) and ('edu_experience' in expert):
        edu_list = expert['edu_experience']
        for edu_bg in edu_list:
            if 'university' in edu_bg and edu_bg['university'] != '':
                expert['graduate_university'] = ""
                expert['graduate_university'] += (edu_bg['university'] + ';')

    col_str, value_str = [], []
    for crawlKey, colName in crawlKey2col.items():
        if crawlKey in expert:
            col_str.append(colName)
            value_str.append("'" + str(expert[crawlKey]).replace("'", "\\'") + "'") # 别忘记转义其中的单引号

    col_str = ','.join(col_str)
    value_str = ','.join(value_str)
    sql = "insert into inventors_crawl(" + col_str + ") values (" + value_str + ")"
    return sql


db = local_db(database='report', datasource='local')

info_list = read_file('2023-03-26')
for info in tqdm(info_list):
    q_sql = f"select inventor_id from inventors_crawl where inventor_id={info['inventor_id']}"
    insert_sql = insert_sql_gen(info)
    if db.query_one(q_sql) is None:
        db.db_edit(insert_sql)

db.db_close()
