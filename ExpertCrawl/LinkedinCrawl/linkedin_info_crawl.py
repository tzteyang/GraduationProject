import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from ExpertCrawl.utils.selenium_tool import selenium_entity
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
    # print(Cookies)
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
    username_el.send_keys('yuqiyang524@gmail.com')
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
    with open(login_path, mode='w') as f:
        f.write(str(Cookies))

    window.browser_close()


def linkedin_info_get_run(window, experts_list):
    # Cookies_get()
    write_path = BASE_DIR + f'/experts_info_{current_date}.json'

    for expert in experts_list:

        if 'linkedin_url' not in expert:
            continue

        window.browser_run(url=expert['linkedin_url'])
        time_sleep(1.75, 2)
        Cookies_add(window)
        time_sleep(1, 1.5)
        window.browser.refresh()
        # time_sleep(0.5, 1)
        # login_el = window.browser.find_elements(By.XPATH, '//a[@data-tracking-control-name="login"]')[0]
        # login_el.click()
        # time_sleep(1.5, 2)
        # username_el = window.browser.find_elements(By.XPATH, '//*[@id="username"]')[0]
        # username_el.send_keys('yuqiyang524@gmail.com')
        # time_sleep(0.5, 0.6)
        # password_el = window.browser.find_elements(By.XPATH, '//*[@id="password"]')[0]
        # password_el.send_keys('yang.8302')
        # time_sleep(0.5, 0.6)
        # confirm_el = window.browser.find_elements(By.XPATH, '//div[@class="login__form_action_container "]')[0]
        # confirm_el.click()

        linkedin_info = {
            'id': expert['inventor_id'],
            'name': expert['inventor_name'],
            'institute': expert['full_name'],
            'simply_institute': expert['short_name'],
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
        expert['work_experience'] = linkedin_info['work_experience']
        expert['edu_experience'] = linkedin_info['edu_experience']
        expert['position'] = linkedin_info['position']
        edu_list = linkedin_info['edu_experience']
        for edu_bg in edu_list:
            if 'degree' in edu_bg:
                if '博士' in edu_bg['degree']:
                    expert['edu_background'] = '博士'
                elif ('Doctor' in edu_bg['degree']) or ('doctor' in edu_bg['degree']):
                    expert['edu_background'] = '博士'
                elif '硕士' in edu_bg['degree']:
                    expert['edu_background'] = '硕士'
                elif ('Master' in edu_bg['degree']) or ('master' in edu_bg['degree']):
                    expert['edu_background'] = '硕士'
                elif '本科' in edu_bg['degree']:
                    expert['edu_background'] = '本科'
                elif ('Bachelor' in edu_bg['degree']) or ('bachelor' in edu_bg['degree']):
                    expert['edu_background'] = '本科'
        # print(expert)

        data_in = json.dumps(linkedin_info, ensure_ascii=False)
        with open(write_path, 'a', encoding='utf-8') as f:
            f.write(data_in)
            f.write('\n')


if __name__ == '__main__':

    pass


