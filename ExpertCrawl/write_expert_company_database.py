from ExpertGraph.utils.db_conn import local_db
from utils.InstitudeSimplify import get_short_name
from tqdm import tqdm
import json
import sys
from pathlib import Path
# 当前项目路径获取
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
DATA_DIR = BASE_DIR + '/SummaryData/input/experts_in.json'


def expert_company_info_in_database():
    db = local_db(database='report', datasource='local')
    expert_com_list = []
    with open(DATA_DIR, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            expert_com_list.append(json.loads(line))
    # print(len(expert_com_list))
    for expert_com in tqdm(expert_com_list):
        if expert_com['full_name'] == '':
            expert_com['full_name'] = '暂无公司名'
        if expert_com['short_name'] == '':
            expert_com['short_name'] = '暂无公司名'
        name_and_t_sql = f"""
            select inventor_name, T_index
            from inventors
            where inventor_id={expert_com['inventor_id']}
        """
        result = db.query_one(name_and_t_sql)
        name, t = result['inventor_name'], result['T_index']
        insert_sql = f"""
            insert into inventors_company
            (inventor_id, inventor_name, company_id, full_name, short_name, T_index) 
            values 
            ('{expert_com["inventor_id"]}', '{name}', '{expert_com["company_id"]}', '{expert_com["full_name"]}', '{expert_com["short_name"]}', '{t}')
        """
        db.db_edit(insert_sql)


def expert_company_info_in_local():

    db = local_db(database='report', datasource='local')

    sql = """
        select inventor_id, inventor_companys
        from inventors
    """
    results = db.query_all(sql)
    # print(results)

    company_info = []

    for com_info in results:
        com_list = []
        expert_id = com_info['inventor_id']
        companys = eval(com_info['inventor_companys'])
        for com_id, count_info in companys.items():
            com_id = eval(com_id)
            count = count_info['patents_num']
            com_list.append((com_id, count))
        com_list.sort(key=lambda x: x[1], reverse=True)
        # print(com_list)
        company_id = com_list[0][0]
        expert = {
            'inventor_id': expert_id,
            'company_id': company_id
        }
        company_info.append(expert)

    # print(company_info)
    db.db_close()

    remote_db = local_db(database='Report', datasource='suwen')

    for expert_com in tqdm(company_info):
        expert_com['full_name'], expert_com['short_name'] = '', ''
        remote_sql = f"""
            select full_name, short_name 
            from company
            where id={expert_com['company_id']}
        """
        result = remote_db.query_one(remote_sql)
        if result is None:
            print(f'\nerror: {expert_com} 暂无公司名')
            data_in = json.dumps(expert_com, ensure_ascii=False)
            with open(DATA_DIR, 'a', encoding='utf-8') as f:
                f.write(data_in + '\n')
            continue
            # break
        if result['short_name'] == '':
            result['short_name'] = get_short_name(result['full_name'])
        expert_com['full_name'] = result['full_name']
        expert_com['short_name'] = result['short_name']
        print(f'\n当前处理专家成功:\n{expert_com}')
        data_in = json.dumps(expert_com, ensure_ascii=False)
        with open(DATA_DIR, 'a', encoding='utf-8') as f:
            f.write(data_in + '\n')

    remote_db.db_close()


expert_company_info_in_database()