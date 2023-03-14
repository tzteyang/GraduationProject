import json
import os
import jsonlines

base_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = base_path + '/ExpertCrawl/BaikeCrawl/output/baike_scholar_info.jsonl'

scholar_list = list(jsonlines.open(data_path))

# print(len(scholar_list))

data_count = 0

# position_count, work_exp_count, edu_exp_count = 0, 0, 0

for baike_schloar in scholar_list:

    data_count = data_count + 1 if 'data' in baike_schloar else data_count
# # 
print(f'专家百科信息存在 {data_count} 条, 概率为{data_count * 0.1}')