import json
import networkx as nx
import sys
from PageRank import page_rank
from ExpertGraph.utils.FunctionTools import scale_function
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt

BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
GRAPH_DIR = BASE_DIR + '/experts_ipcs_output/experts_graph.gml'
IPCS_DIR = BASE_DIR + '/experts_ipcs_output/ipcs_list.txt'
PR_DIR = BASE_DIR + '/experts_ipcs_output/pr_results.json'
print(BASE_DIR)

# 涉及到的专利号列表
ipcs_list = []
with open(IPCS_DIR, 'r', encoding='utf-8') as f:
    ipcs_list = eval(f.readline())

print('合作网络本地读取中...')
G = nx.read_gml(GRAPH_DIR, label='label')
print('合作网络本地读取完成!!!')

all_nodes = G.number_of_nodes()
# 联通分量个数 => 77
"""
在对不同联通分量的节点pagerank值进行对比时，考虑其子图在全图中的大小占比作为一个
重要性权值，如每个节点分别求得的pagerank值相乘，即可使得最终的pr值较为可信
"""


def calculate_in_ipc(current_ipc: str):
    """
    在给定领域内的迭代
    param: 领域IPC号
    return: 本次迭代的各专家评分
    """
    whole_pagerank_vector = {}
    connected_components = nx.connected_components(G)
    cur_pagerank_alg = page_rank()
    # 求出在当前IPC分类下图的个性化向量
    cur_pagerank_alg.personal_vector(current_ipc)
    for index, G_cc in enumerate(connected_components):
        G_subgraph = G.subgraph(G_cc)
        # print('=' * 20 + f'Subgraph {index}' + '=' * 20 + '\n')
        sub_nodes = G_subgraph.number_of_nodes()
        w_sub = sub_nodes / all_nodes
        cur_pagerank_alg.G = G_subgraph
        # print(cur_pagerank_alg.PersonalVector)
        cur_pagerank_vector = cur_pagerank_alg.run(personalization=cur_pagerank_alg.PersonalVector)
        # 对向量进行权重化处理
        pagerank_vector = {key: value * w_sub for key, value in cur_pagerank_vector.items()}
        # 合并各个子图一起分析
        whole_pagerank_vector.update(pagerank_vector)
    # 排除领域节点的影响
    for ipc in ipcs_list:
        whole_pagerank_vector.pop(ipc, None)

    pagerank_score = scale_function(whole_pagerank_vector)
    pagerank_score = dict(sorted(pagerank_score.items(), key=lambda x: x[1], reverse=True)[:100])
    # print('\n', pagerank_score)
    return pagerank_score


def run():
    print('@' * 15 + '开始迭代pagerank' + '@' * 15)

    all_info = {}

    for ipc_id in tqdm(ipcs_list):
        print('\n' + '=' * 15 + f'当前处理IPC号: {ipc_id}' + '=' * 15)
        cur_ipc_result = calculate_in_ipc(ipc_id)
        all_info[ipc_id] = cur_ipc_result

    data_in = json.dumps(all_info, ensure_ascii=False, indent=4)
    with open(PR_DIR, 'w', encoding='utf-8') as f:
        f.write(data_in)

    print('@' * 15 + '迭代pagerank结束' + '@' * 15)


if __name__ == '__main__':
    run()
    # calculate_in_ipc('B65')
