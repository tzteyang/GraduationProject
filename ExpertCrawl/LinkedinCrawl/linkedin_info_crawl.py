import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
from lxml import etree
from Levenshtein import ratio
import os
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


def time_sleep(a, b):
    '''
    :param a:
    :param b:
    :return:
    '''
    time.sleep(random.uniform(a, b))

def Cookies_read():
    '''
    :return: 本地读取cookie
    '''
    login_path = BASE_DIR + '/login_cookies.txt'

    with open(login_path,mode='r') as f:
        Cookies = f.readline()
    return Cookies

def Cookies_add(window):

    Cookies = eval(Cookies_read())
    for cookie in Cookies:
        # print(type(cookie))
        window.browser.add_cookie(cookie)

def Cookies_get():
    '''
    登陆cookies信息的获取 -> 后续免验证和密码登陆
    :return:
    '''
    window = selenium_entity(url='https://www.linkedin.cn/login')
    window.browser_run()
    time_sleep(2, 2.5)
    username_el = window.browser.find_elements(By.XPATH, '//*[@id="username"]')[0]
    username_el.send_keys('15065629195')
    time_sleep(0.5, 1)
    password_el = window.browser.find_elements(By.XPATH, '//*[@id="password"]')[0]
    password_el.send_keys('yang.8302')
    time_sleep(1, 1.5)
    confirm_el = window.browser.find_elements(By.XPATH, '//div[@class="login__form_action_container "]')[0]
    confirm_el.click()
    # time_sleep(2, 2.5)

    # 获取cookies
    login_path = BASE_DIR + '/login_cookies.txt'

    Cookies = window.browser.get_cookies()
    with open(login_path,mode='w') as f:
        f.write(str(Cookies))

    window.browser_close()

def linkedin_info_get_run(window, experts_list):

    write_path = BASE_DIR + f'/experts_info_{current_date}.json'

    # experts_list = []
    # with open(data_path,'r',encoding='utf-8') as f:
    #     for line in f.readlines():
    #         data_out = json.loads(line)
    #         experts_list.append(data_out)

    for expert in experts_list:

        if 'linkedin_url' not in expert:
            continue

        window.browser_run(url=expert['linkedin_url'])
        time_sleep(0.5, 1)
        login_el = window.browser.find_elements(By.XPATH, '//a[@data-tracking-control-name="login"]')[0]
        login_el.click()
        time_sleep(1.5, 2)
        username_el = window.browser.find_elements(By.XPATH, '//*[@id="username"]')[0]
        username_el.send_keys('15065629195')
        time_sleep(0.5, 0.6)
        password_el = window.browser.find_elements(By.XPATH, '//*[@id="password"]')[0]
        password_el.send_keys('yang.8302')
        time_sleep(0.5, 0.6)
        confirm_el = window.browser.find_elements(By.XPATH, '//div[@class="login__form_action_container "]')[0]
        confirm_el.click()

        linkedin_info = {
            'id': expert['id'],
            'name': expert['name'],
            'institute': expert['scholar_institute'],
            'simply_institute': expert['simply_institute'],
            'position': expert['linkedin_position'],
            'work_experience': [],
            'edu_experience': [],
            'url': expert['linkedin_url']
        }

        time_sleep(2.5, 3)
        try:
            work_exp_list = window.browser.find_elements(By.XPATH, '//div[@data-testid="test-index-experience-section"]')

            if work_exp_list:
                # 通用的工作经历div块
                work_el_list = work_exp_list[0].find_elements(By.XPATH, './/div[contains(@class,"ProfileExperiencesCard_experienceBottomLine__+VHhU ProfileExperiencesCard")]')

                for work_el in work_el_list:

                    # 先检查是否在同一公司内存在多段任职经历 会涉及到后面的class=ml24先做判断
                    work_el_divided = work_el.find_elements(By.XPATH, './/div[contains(@class,"ml48")]')
                    if work_el_divided:
                        for work_el in work_el_divided:
                            temp_list = work_el.text.split('\n')
                            # 存储信息的字典
                            user_info = {}

                            user_info['position'] = temp_list[0] if temp_list else ''
                            user_info['company'] = temp_list[1] if len(temp_list) > 1 else ''
                            user_info['duration'] = temp_list[2] if len(temp_list) > 2 else ''
                            user_info['address'] = temp_list[3] if len(temp_list) > 3 else ''

                            linkedin_info['work_experience'].append(user_info)
                            continue

                    # 检查是否存在普通的工作任职经历
                    work_el_common = work_el.find_elements(By.XPATH, './/div[@class="ml24"]')
                    if work_el_common:
                        temp_list = work_el_common[0].text.split('\n')
                        # 存储信息的字典
                        user_info = {}

                        user_info['position'] = temp_list[0] if temp_list else ''
                        user_info['company'] = temp_list[1] if len(temp_list) > 1 else ''
                        user_info['duration'] = temp_list[2] if len(temp_list) > 2 else ''
                        user_info['address'] = temp_list[3] if len(temp_list) > 3 else ''

                        linkedin_info['work_experience'].append(user_info)


        except Exception as e:
            print("errException：", str(e))

        # print(linkedin_info)

        try:
            edu_exp_list = window.browser.find_elements(By.XPATH, '//div[@data-testid="test-index-education-section"]')

            if edu_exp_list:
                # print(edu_exp_list)
                edu_el_list = edu_exp_list[0].find_elements(By.XPATH, './/div[contains(@class,"ProfileExperiencesCard_experienceBottomLine__+VHhU ProfileExperiencesCard")]')
                # print(edu_el_list)
                for edu_el in edu_el_list:
                    edu_el_common = edu_el.find_elements(By.XPATH, './/div[contains(@class,"Index_content__jfYtt")]')
                    temp_list = edu_el_common[0].text.split('\n')
                    # 存储信息的字典
                    edu_info = {}

                    edu_info['university'] = temp_list[0] if temp_list else ''
                    edu_info['degree'] = temp_list[1] if len(temp_list) > 1 else ''
                    edu_info['duration'] = temp_list[2] if len(temp_list) > 2 else ''

                    linkedin_info['edu_experience'].append(edu_info)
        except Exception as e:
            print("errException：", str(e))

        try:
            position_list = window.browser.find_elements(By.XPATH, './/p[@data-testid="data-test-profile-basic-card-headline"]')

            if position_list and (' ' in position_list[0].text):
                position_el = position_list[0].text
                linkedin_info['position'] = position_el
        except Exception as e:
            print("errException：", str(e))

        # print(f'\n{linkedin_info["name"]} {linkedin_info["institute"]} 信息已获取')
        expert['scholar_job_info'] = linkedin_info['work_experience']
        expert['scholar_history'] = linkedin_info['edu_experience']
        expert['occupation'] = linkedin_info['position']
        edu_list = linkedin_info['edu_experience']
        for edu_bg in edu_list:
            if 'degree' in edu_bg:
                if '博士' in edu_bg['degree']:
                    expert['edu_level'] = '博士'
                elif 'Doctor' or 'doctor' in edu_bg['degree']:
                    expert['edu_level'] = '博士'
                elif '硕士' in edu_bg['degree']:
                    expert['edu_level'] = '硕士'
                elif 'Master' or 'master' in edu_bg['degree']:
                    expert['edu_level'] = '硕士'
                elif '本科' in edu_bg['degree']:
                    expert['edu_level'] = '本科'
                elif 'Bachelor' or 'bachelor' in edu_bg['degree']:
                    expert['edu_level'] = '本科'
        # print(expert)
        # print('='*30)

        data_in = json.dumps(linkedin_info, ensure_ascii=False)
        with open(write_path,'a', encoding='utf-8') as f:
            f.write(data_in)
            f.write('\n')


if __name__ == '__main__':

    # 请在使用前获取新的cookie
    # Cookies_get()
    # linkedin_info_get_run()
    pass


