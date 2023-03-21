import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
from lxml import etree
from Levenshtein import ratio
import pandas as pd
from pypinyin import lazy_pinyin
import os
import requests
import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

class selenium_entity():

    def __init__(self, **kwargs):

        self.url = kwargs.get('url')
        self.headless = kwargs.get('headless')
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('detach', True)  #不自动关闭浏览器
        if self.headless:
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')

        self.browser = webdriver.Chrome(options=self.options)

    def browser_run(self, **kwargs):

        if kwargs:
            self.browser.get(kwargs.get('url'))
        else:
            self.browser.get(self.url)

    def browser_close(self):

        self.browser.close()

def linkedin_bing_simply(s):
    s = s.rstrip(' ...')
    s = s.rstrip('| LinkedIn')
    s = s.rstrip('| 职业档案')
    s = s.rstrip('有限公司')
    s = s.rstrip('集团')
    s = s.rstrip('股份')
    s = s.rstrip('控股')
    return s

def time_sleep(a, b):
    '''
    :param a:
    :param b:
    :return:
    '''
    time.sleep(random.uniform(a, b))

def texsmart_query(q1, q2, q_alg):

    obj = {
        'text_pair_list': [{'str1': q1, 'str2': q2}],
        'options': {'alg': q_alg},
        'echo_data': {'id': 123}
    }

    reg_str = json.dumps(obj).encode()
    url = "https://texsmart.qq.com/api/match_text"
    r = requests.post(url, data=reg_str).json()
    ret_code = r["header"]["ret_code"]
    while ret_code != "succ":
        r = requests.post(url, data=reg_str).json()
        ret_code = r["header"]["ret_code"]

    return r['res_list'][0]['score']

def check_sim(s1, s2):

    esim_sim, linkage_sim = texsmart_query(s1, s2, 'esim'), texsmart_query(s1, s2, 'linkage')
    sim = esim_sim * 0.6 + linkage_sim * 0.4
    
    return sim


def search_expert(window, info: dict):
    # 限制域名
    site = 'https://cn.linkedin.com/in'

    input_el = window.browser.find_elements(By.XPATH, '//*[@id="sb_form_q"]')[0]

    search_statement = f"site:{site} {info['inventor_name']} {info['short_name']}"

    input_el.send_keys(search_statement)
    time_sleep(0.5, 1)
    input_el.send_keys(Keys.ENTER)


def search_results_get(window, info: dict):

    search_results = []
    bing_li_list = window.browser.find_elements(By.XPATH, '//li[@class="b_algo"]')

    if bing_li_list:
        rank = 0
        for bing_li in bing_li_list:
            rank += 1
            #尝试请求
            try:
                search_info = {"id": info["inventor_id"], "name": info["inventor_name"], 'institute': info["full_name"], "simply_institute": info['short_name']}
                # print(id(search_info))
                title_el = bing_li.find_elements(By.XPATH, './/div[@class="b_title"]/h2/a')
                abstract_el = bing_li.find_elements(By.XPATH, './/div[contains(@class,"b_vlist2col")]')
                url_el = bing_li.find_elements(By.XPATH, './/cite')

                if title_el:
                    el_text = title_el[0].text.split(' - ')
                    # print(el_text)
                    name, company = el_text[0], el_text[-1]
                    position = el_text[1] if len(el_text) > 2 else ''
                    company = linkedin_bing_simply(company)
                    en_name = zh_name_to_en_name(info['inventor_name'])
                    # print(en_name, name)
                    if name != info['inventor_name'] and name != en_name:
                        continue
                    # 消除一些无意义的称谓词
                    info_company = info['short_name'].replace('控股', '')
                    info_company = info_company.replace('股份', '')
                    info_company = info_company.replace('中国', '')

                    sim = check_sim(info_company, company)
                    # print('\n' + '=' * 15 + '相似度' + '=' * 15)
                    # print(info_company, company, sim)
                    if info_company in company or sim > 0.35:
                        search_info['score'] = sim + (10 - rank) * 0.05
                        search_info['url'] = url_el[0].text if url_el else ''
                        search_info['linkedin_position'] = position
                        search_results.append(search_info)
                    elif abstract_el:
                        abstract = abstract_el[0].text
                        # 删除地理位置信息的影响
                        d = abstract.find('位置')
                        abstract = abstract[:d]
                        # print(abstract)
                        sim = check_sim(info_company, abstract)
                        if info_company in abstract or sim > 0.3:
                            search_info['score'] = sim + (10 - rank) * 0.05
                            search_info['url'] = url_el[0].text if url_el else ''
                            search_info['linkedin_position'] = position
                            search_results.append(search_info)

            except Exception as e:
                print("errException：", str(e))
                continue

    search_results = sorted(search_results, key=lambda x: x['score'], reverse=True)
    # print('\n', search_results)
    return search_results


def zh_name_to_en_name(s):

    name_list = lazy_pinyin(s)
    # print(name_list)
    xing = name_list[0]
    ming = ''
    for el in name_list[1:]:
        ming += el

    en_name = ming + ' ' + xing
    return en_name.title().lstrip()


def linkedin_url_get_run(window, experts_list):
    # 当前路径的父路径
    data_path = BASE_DIR + '/experts_input.json'
    write_path = BASE_DIR + f'/experts_url_{current_date}.json'

    for expert in experts_list:

        window.browser_run(url='https://cn.bing.com/')
        time_sleep(1, 1.2)
        search_expert(window, expert)
        time_sleep(1.5, 2)
        url_results = search_results_get(window, expert)

        if url_results:
            print('\n当前专家领英url已获取')
            expert['linkedin_url'] = url_results[0]['url']
            expert['linkedin_position'] = url_results[0]['linkedin_position']
            data_in = json.dumps(url_results[0], ensure_ascii=False)
            with open(write_path, 'a', encoding='utf-8') as f:
                f.write(data_in)
                f.write('\n')


if __name__ == '__main__':
    # linkedin_url_get_run()
    pass
