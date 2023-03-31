import json
import sys
import matplotlib.pyplot as plt
from pathlib import Path
from ExpertGraph.utils.db_conn import local_db
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
IPC_DIR = str(Path(BASE_DIR).parent) + '/experts_ipcs_output/experts_ipcs_info.json'


def get_axis_data(ipc_id):
    id2ipc = {}
    with open(IPC_DIR, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            id2ipc.update(json.loads(line))

    db = local_db(database='report', datasource='local')
    query_sql = f"select inventor_id, PR_value from ipc_relevant_experts where ipc_id='{ipc_id}'"
    results = db.query_all(query_sql)
    db.db_close()

    count_value, pr_value = [], []
    for item in results:
        key_id = str(item['inventor_id'])
        if ipc_id not in id2ipc[key_id]:
            continue
        count = id2ipc[key_id][ipc_id]
        count_value.append({'inventor_id': item['inventor_id'], 'count': count})
        pr_value.append(item)

    return count_value, pr_value


def figure_draw():
    C = ['C07', 'C09', 'C22', 'C12']
    H = ['H01', 'H02', 'H04', 'H05']
    color = ['blue', 'green', 'red', 'yellow']

    x, y = [], []
    for C_ipc in C:
        pair = get_axis_data(C_ipc)
        tx = [item['count'] for item in pair[0]]
        ty = [item['PR_value'] for item in pair[1]]
        x.append(tx)
        y.append(ty)
    for index in range(len(color)):
        plt.plot(x[index], y[index], color=color[index], label=C[index])

    plt.title('PC --- TI')
    plt.xlabel('Patent Count')
    plt.ylabel('Technology Influence')

    plt.legend()
    plt.savefig('./figure_show_in_C_domain.png')
    plt.show()


if __name__ == '__main__':
    figure_draw()




