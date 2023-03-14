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

position_count, work_exp_count, edu_exp_count = 0, 0, 0

for expert_info in experts_info_list:

    position_count = position_count + 1 if expert_info['position'] != '' else position_count
    work_exp_count = work_exp_count + 1 if expert_info['work_experience'] != [] else work_exp_count
    edu_exp_count = edu_exp_count + 1 if expert_info['edu_experience'] != [] else edu_exp_count

print(f'职位信息存在 {position_count} 条, 概率为{position_count * 0.1}; 工作经历存在 {work_exp_count} 条, 概率为{work_exp_count * 0.1}; 教育经历存在 {edu_exp_count} 条, 概率为{edu_exp_count * 0.1}')