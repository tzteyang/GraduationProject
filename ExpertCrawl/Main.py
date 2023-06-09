from ExpertCrawlRun import ExpertCrawlRun
import json
import sys
import time
from pathlib import Path
# 当前项目路径获取
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
DATA_DIR = BASE_DIR + f'/SummaryData/output/all_experts_info_{current_date}.json'

if __name__ == '__main__':
    # 将代码push到github仓库会被openai检测到api泄露自动轮换 push的时候切记不用push SentenceSimilarity.py这个文件
    cur_crawl_run = ExpertCrawlRun(DATA_DIR)
    # print(cur_crawl_run.data_list)
    cur_crawl_run.fetch_expert_info()
