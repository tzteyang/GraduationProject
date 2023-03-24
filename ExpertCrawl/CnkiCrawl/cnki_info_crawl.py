import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
from lxml import etree
from Levenshtein import ratio
import re
import os
import pandas as pd
import sys
from pathlib import Path

current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
WRITE_DIR = BASE_DIR + f'/experts_info_{current_date}.json'


class selenium_entity():

    def __init__(self, **kwargs):

        self.url = kwargs.get('url')
        self.headless = kwargs.get('headless')
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('detach', True)  # 不自动关闭浏览器
        if self.headless:
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')

        self.browser = webdriver.Chrome(options=self.options)

    def browser_run(self, **kwargs):

        if kwargs:
            self.url = kwargs.get('url')
        self.browser.get(self.url)

    def browser_close(self):

        self.browser.close()


def time_sleep(a, b):
    time.sleep(random.uniform(a, b))


def user_login(window, acc, pwd):
    # 每个用户每天只能查看200个学者的主页
    login_el = window.browser.find_elements(By.XPATH, '//span[@name="loginSpan"]/a[@id="link_login"]')[0]
    login_el.click()
    user_input_el = window.browser.find_elements(By.XPATH, '//input[@id="username"]')[0]
    user_input_el.send_keys(acc)
    time_sleep(1, 1.5)
    pwd_input_el = window.browser.find_elements(By.XPATH, '//input[@id="password"]')[0]
    pwd_input_el.send_keys(pwd)
    time_sleep(0.5, 1)
    confirm_el = window.browser.find_elements(By.XPATH, '//input[@id="submittext"]')[0]
    confirm_el.click()


def user_exit(window):
    exit_el = window.browser.find_elements(By.XPATH, '//a[@class="exit"]')[0]
    exit_el.click()
    time_sleep(1, 1.5)


def login_list_get():
    data_path = BASE_DIR + f'/cnki_login.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        data_out = json.load(f)

    return data_out


def cnki_info_get_run(window, experts_list, cur_index):
    cur_index += 500
    # 账号列表
    login_list = login_list_get()

    for expert in experts_list:
        p = (cur_index // 200) % 5
        print('@' * 10 + "爬取知网学者库信息中..." + '@' * 10 + '\n', cur_index, p)
        # 每200个专家切换一次账号
        if (cur_index and cur_index % 200 == 0) or (cur_index and cur_index % 25 == 0):
            # window = selenium_entity(headless=True)
            window.browser_run(url='https://expert.cnki.net/')
            time_sleep(4, 4.5)
            user_exit(window)
            time_sleep(1, 1.5)
            user_login(window, login_list[p]["account"], login_list[p]["password"])
            time_sleep(2, 2.5)

        cnki_info = {
            'id': expert['inventor_id'],
            'name': expert['inventor_name'],
            'institute': expert['full_name'],
            'simply_institute': expert['short_name'],
            'research_field': '',
            'domain': '',
            'download': 0,
            'refer': 0,
            'url': expert['cnki_url']
        }

        # url为空
        if cnki_info['url'] == '':
            data_in = json.dumps(cnki_info, ensure_ascii=False)
            with open(WRITE_DIR, 'a', encoding='utf-8') as f:
                f.write(data_in)
                f.write('\n')
            continue

        window.browser_run(url=expert['cnki_url'])
        # 等待时间过短会导致专家专利下载等信息未加载完毕
        time_sleep(6, 7)

        research_field_list = window.browser.find_elements(By.XPATH, '//div[@id="headResearchField"]')
        cnki_info['research_field'] = research_field_list[0].text if research_field_list else ''

        domain_list = window.browser.find_elements(By.XPATH, '//p[@id="domian-list"]')
        cnki_info['domain'] = domain_list[0].text if domain_list else ''

        num_list = window.browser.find_elements(By.XPATH, '//p[@class="item_info item_moreinfo"]/span[1]')

        obj = re.compile(r'下载:(?P<download>.*?)次 , 被引:(?P<refer>.*?)次', re.S)

        for num_el in num_list:
            result = obj.finditer(num_el.get_attribute('outerHTML'))
            for item in result:
                cnki_info['download'] += int(item.group('download'))
                cnki_info['refer'] += int(item.group('refer'))

        if cnki_info['domain'] == '':
            print(f'Error: {cnki_info["name"]}-{cnki_info["institute"]}-页面获取失败')
            print('=' * 30)

        expert['research_field'] = cnki_info['research_field']
        expert['domain'] = cnki_info['domain']
        expert['download'] = cnki_info['download']
        expert['refer'] = cnki_info['refer']

        data_in = json.dumps(cnki_info, ensure_ascii=False)
        with open(WRITE_DIR, 'a', encoding='utf-8') as f:
            f.write(data_in)
            f.write('\n')

        print('\n', expert)
        print('='*30)


if __name__ == '__main__':
    pass
