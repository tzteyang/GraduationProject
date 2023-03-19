import pymysql
import json
import sys
from pathlib import Path
from ExpertGraph.utils.db_conn import local_db

BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
PR_DIR = BASE_DIR + '/experts_ipcs_output/pr_results.json'

with open(PR_DIR, 'r', encoding='utf-8') as f:
    ipcs_top_info = json.load(f)

db = local_db(database='report', datasource='local')

for ipc, top_info in ipcs_top_info.items():
    for expert_id, pr_value in top_info.items():
        expert_id = eval(expert_id)
        sql = f"""
            insert into ipc_relevant_experts
            (ipc_id, inventor_id, PR_value)
            values ('{ipc}', '{expert_id}', '{pr_value}')
        """
        db.db_edit(sql)

db.db_close()
