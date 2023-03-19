import json
import sys
import numpy as np
import scipy as sp
import scipy.sparse
from pathlib import Path
import networkx as nx

BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
DATA_DIR = BASE_DIR + '/experts_ipcs_output/experts_ipcs_info.json'
IPC_WRITE_DIR = BASE_DIR + '/experts_ipcs_output/ipcs_info.json'


class page_rank:

    def __init__(self):
        self.PersonalVector = None
        self.G = None

    def personal_vector(self, topic: str):  # 获取当前领域下的特征向量
        # 从本地读取当前领域的专利总数
        local_ipcs_info = {}
        with open(IPC_WRITE_DIR, 'r', encoding='utf-8') as f:
            local_ipcs_info = json.load(f)
        cur_topic_total = local_ipcs_info[topic]['total']
        # print(cur_topic_total)
        # print('=' * 30)
        # 从本地读取每个专家涉及领域的信息
        experts_ipc_list = []
        with open(DATA_DIR, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                data_out = json.loads(line)
                experts_ipc_list.append(data_out)

        index = 0
        personal = {}
        for expert_ipc in experts_ipc_list:
            index += 1
            for expert_id, ipc_info in expert_ipc.items():
                # expert_id = eval(expert_id)
                # print(f'当前正在处理领域信息专家id: {expert_id}, 进度 {index} / {len(experts_ipc_list)}')
                if topic in ipc_info:
                    personal[expert_id] = ipc_info[topic]
                else:
                    personal[expert_id] = 0
        # 返回当前领域下的每个点的个性化向量值
        for ipc in local_ipcs_info.keys():
            personal[ipc] = 0

        self.PersonalVector = personal
        # print(self.PersonalVector)

    def run(self, alpha=0.85, personalization=None, max_iter=100, tol=1.0e-6, nstart=None, weight="weight", dangling=None):

        N = len(self.G)
        if N == 0:
            return {}

        nodelist = list(self.G)
        A = nx.to_scipy_sparse_array(self.G, nodelist=nodelist, weight=weight, dtype=float)
        S = A.sum(axis=1)
        S[S != 0] = 1.0 / S[S != 0]
        # TODO: csr_array
        Q = sp.sparse.csr_array(sp.sparse.spdiags(S.T, 0, *A.shape))
        A = Q @ A

        # initial vector
        if nstart is None:
            x = np.repeat(1.0 / N, N)
        else:
            x = np.array([nstart.get(n, 0) for n in nodelist], dtype=float)
            x /= x.sum()

        # Personalization vector
        if personalization is None:
            p = np.repeat(1.0 / N, N)
        else:
            p = np.array([personalization.get(n, 0) for n in nodelist], dtype=float)
            # 当前子图在迭代IPC下未有涉及 平均化个性向量即可
            if p.sum() == 0:
                p = np.repeat(1.0, N)
            p /= p.sum()
        assert (abs(p.sum() - 1)) < 1e-5
        # Dangling nodes
        if dangling is None:
            dangling_weights = p
        else:
            # Convert the dangling dictionary into an array in nodelist order
            dangling_weights = np.array([dangling.get(n, 0) for n in nodelist], dtype=float)
            dangling_weights /= dangling_weights.sum()
        is_dangling = np.where(S == 0)[0]
        # print('当前图的悬挂节点有:', is_dangling)
        # power iteration: make up to max_iter iterations
        for _ in range(max_iter):
            x_last = x
            x = alpha * (x @ A + sum(x[is_dangling]) * dangling_weights) + (1 - alpha) * p
            # check convergence, l1 norm
            err = np.absolute(x - x_last).sum()
            if err < N * tol:
                return dict(zip(nodelist, map(float, x)))
        raise nx.PowerIterationFailedConvergence(max_iter)
        # 根据当前图和p向量运行pagerank

