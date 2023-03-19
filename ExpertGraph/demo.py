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
IPC_WRITE_DIR = BASE_DIR + '/experts_ipcs_output/ipcs_info.json'
IPCS_DIR = BASE_DIR + '/experts_ipcs_output/ipcs_list.txt'
PR_DIR = BASE_DIR + '/experts_ipcs_output/pr_results.json'

local_ipcs_info = {}
with open(IPC_WRITE_DIR, 'r', encoding='utf-8') as f:
    local_ipcs_info = json.load(f)
ipcs_list = [key for key in local_ipcs_info.keys()]
with open(IPCS_DIR, 'w', encoding='utf-8') as f:
    f.write(str(ipcs_list))