import networkx as nx
import sys
from PageRank import page_rank
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
GRAPH_DIR = BASE_DIR + '/experts_ipcs_output/experts_graph.gml'
print(BASE_DIR)

print('合作网络本地读取中...')
G = nx.read_gml(GRAPH_DIR, label='label')
print('合作网络本地读取完成!!!')

connected_components = nx.connected_components(G)
# 联通分量个数 => 77
"""
在对不同联通分量的节点pagerank值进行对比时，考虑其子图在全图中的大小占比作为一个
重要性权值，如每个节点分别求得的pagerank值相乘，即可使得最终的pr值较为可信
"""

for index, G_cc in enumerate(connected_components):
    G_subgraph = G.subgraph(G_cc)
    cur_pagerank_alg = page_rank(G_subgraph)

    cur_pagerank_alg.personal_vector('H01')
    # print(cur_pagerank_alg.PersonalVector)
    results = cur_pagerank_alg.run()
    print('=' * 20 + f'Subgraph {index} \'s pagerank vector is' + '=' * 20 + '\n', results)
