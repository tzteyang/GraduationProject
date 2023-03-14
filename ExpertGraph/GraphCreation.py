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
DATA_DIR = BASE_DIR + '/experts_ipcs_output/experts_ipcs_info.json'
WRITE_DIR = BASE_DIR + '/experts_ipcs_output/experts_graph.gml'
IPC_WRITE_DIR = BASE_DIR + '/experts_ipcs_output/ipcs_info.json'
print(BASE_DIR)

G = nx.Graph()


def generate_graph_by_collaborators(expert_id, collaborators: dict):
    """
    根据当前专家id和他的合作关系更新图
    :param expert_id:
    :param collaborators:
    :return:
    """
    if not G.has_node(expert_id):
        G.add_node(expert_id)

    for co_id, co_info in collaborators.items():
        co_id = eval(co_id)
        # 强制规范
        if co_id > 35580:
            continue
        if not G.has_edge(expert_id, co_id):
            co_times = len(co_info['times'])
            G.add_weighted_edges_from([(expert_id, co_id, co_times)])


def generate_graph_by_ipc_relation(expert_id, relation_info: dict):
    """
    根据专家和领域的联系生成图
    :param expert_id:
    :param relation_info:
    :return:
    """
    for ipc_id, times in relation_info.items():
        if not G.has_edge(expert_id, ipc_id):
            G.add_weighted_edges_from([(expert_id, ipc_id, times)])


def graph_get_run():

    db = local_db(database='report')

    records = 35580
    experts_get_sql = f'''
        select inventor_id, collaborators
        from inventors
        order by inventor_id 
        limit {records}
    '''

    experts_list = db.query_all(experts_get_sql)
    # ---------------------------通过合作关系建立专家节点及关系---------------------------
    index = 0
    for expert in experts_list:
        index += 1
        print(f'当前正在处理专家id: {expert["inventor_id"]}, 进度 {index} / {records}')
        generate_graph_by_collaborators(expert["inventor_id"], eval(expert['collaborators']))

    # ---------------------------通过领域信息建立领域节点及关系---------------------------

    experts_ipc_list = []
    with open(DATA_DIR, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            data_out = json.loads(line)
            experts_ipc_list.append(data_out)

    index = 0
    for expert_ipc in experts_ipc_list:
        index += 1
        for id, ipc_info in expert_ipc.items():
            id = eval(id)
            print(f'当前正在处理领域信息专家id: {id}, 进度 {index} / {len(experts_ipc_list)}')
            generate_graph_by_ipc_relation(id, ipc_info)

    # for edge in G.edges(data='weight'):
    #     print("Edge:", edge)
    nx.pagerank()
    # 将生成的图存入本地
    nx.write_gml(G, WRITE_DIR)
    # G_A = nx.adjacency_matrix(G).todense()
    # nx.draw(G, with_labels=True, ax=fig.add_subplot(111),node_size=20, font_size=10)
    # plt.show()

    db.db_close()


def test():

    print('='*15+'读取本地图中'+'='*15)
    G = nx.read_gml(WRITE_DIR, label='label')
    print('='*15+'图读取完成'+'='*15)
    print(G.number_of_nodes())
    # print(len(list(nx.connected_components(G))))
    # cc = list(nx.connected_components(G))
    # for i, cc in tqdm(enumerate(nx.connected_components(G))):
    #     g = G.subgraph(cc)
    #     pagerank = nx.pagerank(g)
    #     sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    #     print(f"Subgraph {i}: {sorted_pagerank}")
    # ipcs_info = {}
    # with open(IPC_WRITE_DIR, 'r', encoding='utf-8') as f:
    #     ipcs_info = json.load(f)
    # count = 0
    # for ipc, info in ipcs_info.items():
    #     if G.has_node(ipc):
    #         print(ipc)
    #         count += 1
    # print(count)


if __name__ == '__main__':
    test()
    pass
    # graph_get_run()
