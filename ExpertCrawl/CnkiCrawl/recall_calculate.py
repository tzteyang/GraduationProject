import json
import os
import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
data_path = BASE_DIR + '/experts_info.json'

experts_info_list = []

with open(data_path,'r',encoding='utf-8') as f:

    for line in f.readlines():
        data_out = json.loads(line)
        experts_info_list.append(data_out)

field_count, domain_count, download_count, refer_count = 0, 0, 0, 0

for expert_info in experts_info_list:

    field_count = field_count + 1 if expert_info['research_field'] != '' else field_count
    domain_count = domain_count + 1 if expert_info['domain'] != '' else domain_count
    download_count = download_count + 1 if expert_info['download'] != '' else download_count
    refer_count = refer_count + 1 if expert_info['refer'] != '' else refer_count

print(f'''
研究方向信息存在 {field_count} 条, 概率为{field_count * 0.1}\n
科研领域存在 {domain_count} 条, 概率为{domain_count * 0.1}\n
下载量信息存在 {download_count} 条, 概率为{download_count * 0.1}\n
引用量信息存在 {refer_count} 条, 概率为{refer_count * 0.1}
''')