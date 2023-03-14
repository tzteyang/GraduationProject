import pymysql
import networkx as nx
import sys
import json
import ast
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from utils.db_conn import local_db
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
EXPERT_WRITE_DIR = BASE_DIR + '/experts_ipcs_output/experts_ipcs_info.json'
IPC_WRITE_DIR = BASE_DIR + '/experts_ipcs_output/ipcs_info.json'
print(BASE_DIR)

def data_preprocess(expert_id, pantents_ipcs: dict, ipcs_count_info: dict):
    '''
    预处理出每个专家在各个领域的专利数
    :param expert_id:
    :param pantents_ipc:
    :return:
    '''
    # print(pantents_ipcs)
    # 专家专利数和涉及ipc不对应是因为一个专利会涉及多个ipc分类
    expert_ipcs = {expert_id: {}}
    for ipc, info in pantents_ipcs.items():
        ipc_key, ipc_times = ipc[:3], len(info['time'])
        if ipc_key not in expert_ipcs[expert_id]:
            expert_ipcs[expert_id][ipc_key] = ipc_times
        else:
            expert_ipcs[expert_id][ipc_key] += ipc_times
    # print(expert_ipcs)
    data_in = json.dumps(expert_ipcs, ensure_ascii=False)
    with open(EXPERT_WRITE_DIR, 'a', encoding='utf-8') as f:
        f.write(data_in + '\n')

    for ipc, times in expert_ipcs[expert_id].items():
        if ipc not in ipcs_count_info:
            # 初始化一个字典
            ipcs_count_info[ipc] = {}
            ipcs_count_info[ipc]['total'] = times
            ipcs_count_info[ipc]['relevant_experts'] = [expert_id]
        else:
            ipcs_count_info[ipc]['total'] += times
            ipcs_count_info[ipc]['relevant_experts'].append(expert_id)
    # print(ipcs_count_info)
    # print(len(ipcs_count_info))


def data_get_run():
    '''
    数据处理
    :return:
    '''
    db = local_db(database='report')

    records = 35580 #创建图的专家数
    experts_get_sql = f'''
            select inventor_id, patents_ipcs
            from inventors
            order by inventor_id
            limit {records}
        '''

    experts_list = db.query_all(experts_get_sql)

    ipcs_count_info = {}
    index = 0
    for expert in tqdm(experts_list):
        index += 1
        print('\n','='*15+f'当前正在处理专家id: {expert["inventor_id"]}, 进度 {index} / {records}'+'='*15)
        data_preprocess(expert['inventor_id'], eval(expert['patents_ipcs']), ipcs_count_info)

    data_in = json.dumps(ipcs_count_info, ensure_ascii=False, indent=4)
    with open(IPC_WRITE_DIR, 'w', encoding='utf-8') as f:
        f.write(data_in + '\n')

    db.db_close()


if __name__ == '__main__':
    pass
    # data_get_run()