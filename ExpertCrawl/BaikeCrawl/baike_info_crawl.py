# coding=utf-8
import jsonlines
import requests
import json
import random
import time
import re
import os
import sys
from lxml import etree
from tqdm import tqdm
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
from utils.SentenceTransformer.SentenceSim import top5_sim_sentence
from utils.SeleniumInit import SeleniumInit
from selenium.webdriver.common.by import By
# from utils.SentenceSimilarity import prompt_pretreatment, openai_query, get_key
current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
DATA_FILE = BASE_DIR + f'/output/baike_info_{current_date}.jsonl'


def time_sleep(a, b):
    """等待时间
    Args:
        a (float): _description_.
        b (float): _description_.
    """
    time.sleep(random.uniform(a, b))


def get_el_text(el):
    """获取标签内容"""
    try:
        # 正则去除字符串中的引用部分
        tmp_str = re.sub('\[\d\]', '', etree.HTML(el.get_attribute('innerHTML')).xpath('string(.)').replace('\n', '').replace('\xa0',''))
        return tmp_str
    except Exception as e:
        print("get_el_text_err：-->", str(e))
        return ''


def texsmart_query(q1, q2, q_alg):
    time_sleep(0.5, 1)
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
    # print(r)
    return r['res_list'][0]['score']


def get_word_info(selInit, scholar):
    '''
    获取词条信息
    '''
    # 图集图像
    img_xpath = '//div[@class="summary-pic"]//img'
    # 现任职位
    occupation_xpath = '//div[@class="lemma-desc"]'
    # 简介
    intro_xpath = '//div[@class="lemma-summary"]'
    # 定位标题
    title_xpath = "//div[contains(@class, 'para-title')]"
    # 定位标题下对应的内容
    t_content_xpath = "./following-sibling::div"
    # 对应内容的上一个节点（检索简介，同时区分目录数据）
    pre_xpath = "./preceding-sibling::div[1]"
    intro2_xpath = "//div[@class='para']"
    # 定位basic信息
    base_info_dt_xpath = "//div[contains(@class, 'basic-info')]//dt"
    base_info_dd_xpath = "//div[contains(@class, 'basic-info')]//dd"

    # 符合特征匹配，获取元素
    img_xpath_el = selInit.browser.find_elements(By.XPATH, img_xpath)  # 图像
    intro_el = selInit.browser.find_elements(By.XPATH, intro_xpath)  # 简介
    intro2_el = selInit.browser.find_elements(By.XPATH, intro2_xpath)  # 人物简介2
    occupation_el = selInit.browser.find_elements(By.XPATH, occupation_xpath)  # 职位
    base_info_dt_el = selInit.browser.find_elements(By.XPATH, base_info_dt_xpath)  # basic信息
    base_info_dd_el = selInit.browser.find_elements(By.XPATH, base_info_dd_xpath)  # basic信息
    scholar["data"] = {}
    if base_info_dt_el:
        # 判断基本信息是否存在并抽取
        scholar["data"]["base_info"] = []
        for index, item in enumerate(base_info_dt_el):
            b_title = get_el_text(item).replace(' ', '')
            b_res = get_el_text(base_info_dd_el[index])
            scholar["data"]["base_info"].append({b_title: b_res})
    title_el_list = selInit.browser.find_elements(By.XPATH, title_xpath)  # 标题
    # 获取任务简介
    if intro2_el:
        for el in intro2_el:
            # print(el)
            pre_el = el.find_elements(By.XPATH, pre_xpath)
            pre_class = etree.HTML(pre_el[0].get_attribute('class')).xpath('string(.)') if pre_el else ""
            # print('@'*30+'\n', pre_class, '@'*30+'\n')
            # if "basic-info" in pre_class:
                # 当前内容符合人物简介
            content = get_el_text(el).replace(' ', '')
            scholar["data"]["简介"] = content
    # 写入源url
    scholar["data"]["source_url"] = selInit.browser.current_url
    # 获取简介
    scholar["data"]["intro"] = get_el_text(intro_el[0]) if intro_el else ''
    # 获取图像
    scholar["data"]["img"] = etree.HTML(img_xpath_el[0].get_attribute('src')).xpath('string(.)') if img_xpath_el else ''
    # 获取职业
    scholar["data"]["occupation"] = get_el_text(occupation_el[0])
    # 通过判断title来定位目标标签
    if title_el_list:
        for title_el in title_el_list:
            title = get_el_text(title_el).replace(' ', '').replace('播报', '').replace('编辑', '').replace(scholar["inventor_name"], '').replace('\n', '')
            content_el_list = title_el.find_elements(By.XPATH, t_content_xpath)
            # TODO 截断到下一个title之前，故要把每个的属性拿出来判断是否是title，是则退出
            for content_el in content_el_list:
                try:
                    props = content_el.get_attribute('data-pid')
                    if not props:
                        break
                    content = get_el_text(content_el) if content_el else ''
                    if content:
                        if not title in list(scholar["data"].keys()):
                            scholar["data"][title] = []
                        scholar["data"][title].append(content)
                except Exception as e:
                    print("err：截断目录出错-->", str(e))
                    continue
    return scholar


def check_word(selInit, scholar):
    # 检查是否是多义词(默认选第一个)
    polysemy_xpath = '//li[contains(@class,"list-dot")]//a'
    polysemy_xpath_2 = '//div[contains(@class, "polysemant-list")]//li/a'
    polysemy_list = selInit.browser.find_elements(By.XPATH, polysemy_xpath)
    polysemy_list_2 = selInit.browser.find_elements(By.XPATH, polysemy_xpath_2)

    # 定位百科内容
    content_xpath = "//div[@class='content-wrapper']"
    new_scholar_list = []

    list_cost, check_cost = 0, 0
    start = time.perf_counter()
    if polysemy_list or polysemy_list_2:
        # 多义词
        if polysemy_list:
            # ==> 直接弹出多义选项的情况
            # 遍历多义选项，查看标题是否是否符合特征

            # 存储所有候选多义词条
            candidates = []
            item2url = {}
            for item in polysemy_list:
                try:
                    if item:
                        item_title = etree.HTML(item.get_attribute('innerHTML')).xpath('string(.)').\
                            replace(scholar["inventor_name"], '')
                        url = etree.HTML(item.get_attribute('href')).xpath('string(.)')
                        # ------------------------gpt3.5-turbo匹配------------------------
                        candidates.append(item_title)
                        item2url[item_title] = url

                except Exception as e:
                    print("err：循环匹配多义词条出错--->", e)
                    continue
            # ------------------------Sbert + Texsmart------------------------
            check_start = time.perf_counter()
            sim_preprocess_list = top5_sim_sentence(scholar['full_name'], candidates)
            print(sim_preprocess_list)
            sim_final_list = []
            for candidate in sim_preprocess_list:
                sim = texsmart_query(scholar['short_name'], candidate, 'linkage') * 0.5 + \
                      texsmart_query(scholar['short_name'], candidate, 'esim') * 0.5
                if sim > 0.3:
                    sim_final_list.append((candidate, sim))
            check_end = time.perf_counter()
            check_cost += check_end - check_start
            sim_final_list.sort(key=lambda x: x[1], reverse=True)
            if sim_final_list:
                sim_url = item2url[sim_final_list[0][0]]
                new_scholar = get_word_info(selInit, scholar)
                new_scholar_list.append(new_scholar)
            else:
                # 未有特征匹配上的词条，退出
                scholar["baike_search_log"] = "当前词条是多义词，未有词条匹配"
                new_scholar_list.append(scholar)
            # ------------------------gpt3.5-turbo匹配------------------------
            # # print(item2url)
            # check_start = time.perf_counter()
            # check_prompt = prompt_pretreatment(scholar['full_name'], candidates)
            # answer = openai_query(check_prompt, get_key())
            # # print(answer)
            # # 处理gpt-api的返回结果
            # answer = answer.replace('[', '')
            # answer = answer.replace(']', '')
            # try:
            #     return_json = eval(answer)
            #     if return_json['code'] == 'succ':
            #         choose_sentence = return_json['sentence']
            #         sim = texsmart_query(scholar['full_name'], choose_sentence, 'esim') * 0.5 + \
            #             texsmart_query(scholar['full_name'], choose_sentence, 'linkage') * 0.5
            #         if sim > 0.35:
            #             choose_url = item2url[choose_sentence]
            #             selInit.page_parse(url=choose_url)
            #             time_sleep(1, 2)
            #             new_scholar = get_word_info(selInit, scholar)
            #             new_scholar_list.append(new_scholar)
            #         else:
            #             scholar["baike_search_log"] = "当前词条是多义词，未有词条匹配"
            #             new_scholar_list.append(scholar)
            #     else:
            #         # 未有特征匹配上的词条，退出
            #         scholar["baike_search_log"] = "当前词条是多义词，未有词条匹配"
            #         new_scholar_list.append(scholar)
            # except Exception as e:
            #     print(f'gpt返回结果格式错误: {answer}\n', e)
            # check_end = time.perf_counter()
            # check_cost += check_end - check_start

        if polysemy_list_2:
            # ==> 直接进入词条页面，但还是多义词的情况
            cur_title_xpath = '//div[@class="lemma-desc"]'
            cur_title_el = selInit.browser.find_elements(By.XPATH, cur_title_xpath)
            cur_title = get_el_text(cur_title_el[0])

            cur_url = selInit.browser.current_url
            # ------------------------gpt3.5-turbo匹配------------------------
            item2url = {}
            candidates = []
            item2url[cur_title] = cur_url
            candidates.append(cur_title)
            # 遍历其他多义词条
            for item in polysemy_list_2:
                try:
                    if item:
                        item_title = etree.HTML(item.get_attribute('innerHTML')).xpath('string(.)').replace(scholar["inventor_name"], '')
                        url = etree.HTML(item.get_attribute('href')).xpath('string(.)')
                        # ------------------------gpt3.5-turbo匹配------------------------
                        item2url[item_title] = url
                        candidates.append(item_title)
                except Exception as e:
                    print("err：循环匹配多义词条出错--->", str(e))
                    continue
            # ------------------------Sbert + Texsmart------------------------
            check_start = time.perf_counter()
            sim_preprocess_list = top5_sim_sentence(scholar['full_name'], candidates)
            print(sim_preprocess_list)
            sim_final_list = []
            for candidate in sim_preprocess_list:
                sim = texsmart_query(scholar['short_name'], candidate, 'linkage') * 0.5 + \
                      texsmart_query(scholar['short_name'], candidate, 'esim') * 0.5
                if sim > 0.3:
                    sim_final_list.append((candidate, sim))
            check_end = time.perf_counter()
            check_cost += check_end - check_start
            sim_final_list.sort(key=lambda x: x[1], reverse=True)
            if sim_final_list:
                sim_url = item2url[sim_final_list[0][0]]
                new_scholar = get_word_info(selInit, scholar)
                new_scholar_list.append(new_scholar)
            else:
                # 未有特征匹配上的词条，退出
                scholar["baike_search_log"] = "当前词条是多义词，未有词条匹配"
                new_scholar_list.append(scholar)
            # ------------------------gpt3.5-turbo匹配------------------------
            # print(item2url)
            # check_start = time.perf_counter()
            # check_prompt = prompt_pretreatment(scholar['full_name'], candidates)
            # # print(check_prompt)
            # answer = openai_query(check_prompt, get_key())
            # # 处理gpt-api的返回结果
            # answer = answer.replace('[', '')
            # answer = answer.replace(']', '')
            # try:
            #     return_json = eval(answer)
            #     if return_json['code'] == 'succ':
            #         choose_sentence = return_json['sentence']
            #         sim = texsmart_query(scholar['full_name'], choose_sentence, 'esim') * 0.5 + \
            #             texsmart_query(scholar['full_name'], choose_sentence, 'linkage') * 0.5
            #         if sim > 0.35:
            #             choose_url = item2url[choose_sentence]
            #             selInit.page_parse(url=choose_url)
            #             time_sleep(1, 2)
            #             # TODO 抽取页面数据
            #             new_scholar = get_word_info(selInit, scholar)
            #             new_scholar_list.append(new_scholar)
            #         else:
            #             scholar["baike_search_log"] = "当前词条是多义词，未有词条匹配"
            #             new_scholar_list.append(scholar)
            #     else:
            #         # 未有特征匹配上的词条，退出
            #         scholar["baike_search_log"] = "当前词条是多义词，未有词条匹配"
            #         new_scholar_list.append(scholar)
            # except Exception as e:
            #     print(f'gpt返回结果格式错误: {answer}\n' + str(e))
            # check_end = time.perf_counter()
            # check_cost += check_end - check_start

    else:
        # TODO 单义词 查看是否符合特征
        cur_title_xpath = '//div[@class="lemma-desc"]'
        cur_title_el = selInit.browser.find_elements(By.XPATH, cur_title_xpath)
        cur_title = get_el_text(cur_title_el[0]) if cur_title_el else ''
        # ------------------------Texsmart匹配------------------------
        check_start = time.perf_counter()
        sim = texsmart_query(scholar['short_name'], cur_title, 'linkage') * 0.5 + \
              texsmart_query(scholar['short_name'], cur_title, 'esim') * 0.5
        check_end = time.perf_counter()
        check_cost += check_end - check_start
        # # ------------------------gpt3.5-turbo匹配------------------------
        # candidates = [cur_title]
        # check_start = time.perf_counter()
        # check_prompt = prompt_pretreatment(scholar['full_name'], candidates)
        # answer = openai_query(check_prompt, get_key())
        # check_end = time.perf_counter()
        # check_cost += check_end - check_start
        # answer = answer.replace('[', '')
        # answer = answer.replace(']', '')
        # # 处理gpt-api的返回结果
        # try:
        #     return_json = eval(answer)
        #     if return_json['code'] == 'succ':
        #         # print(return_json)
        #         # choose_sentence = return_json['sentence']
        #         # TODO 抽取页面数据
        #         # print(selInit.browser.current_url)
        #         new_scholar = get_word_info(selInit, scholar)
        #         new_scholar_list.append(new_scholar)
        #     else:
        #         # 未有特征匹配上的词条，退出
        #         scholar["baike_search_log"] = "当前词条是单义词，未有词条匹配"
        #         new_scholar_list.append(scholar)
        # except Exception as e:
        #     print(f'gpt返回结果格式错误: {answer}\n', e)

    end = time.perf_counter()
    list_cost = end - start
    print('=' * 30 + '耗时' + '=' * 30)
    print(list_cost)
    print('=' * 30 + '查询相似度耗时' + '=' * 30)
    print(check_cost)

    return new_scholar_list


def query_word(scholar, selInit):
    """查询词条"""
    query_input_el = selInit.browser.find_elements(By.XPATH, '//input[@id="query"]')
    search_el = selInit.browser.find_elements(By.XPATH, '//button[@id="search"]')
    query_input_el[0].send_keys(scholar["inventor_name"])  # 动作：输入
    time_sleep(1, 2)
    selInit.browser.execute_script("arguments[0].click();", search_el[0])


def insert_data(info_list):
    """数据写入"""
    # 防止出现多条匹配情况，可忽略
    for info in info_list:
        with jsonlines.open(DATA_FILE, 'a') as f:
            f.write(info)


def baike_info_get_run(experts_list):
    # print("@@ 百度百科专家数据爬取")
    url = "https://baike.baidu.com/"

    base_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
    # data_path = base_path + '/ExpertCrawl/experts_input.json'

    scholar_list = []
    for expert in experts_list:
        scholar_list.append(expert)
    # print(id(experts_list), id(scholar_list))
    # 数据入口文件
    # scholar_list = list(jsonlines.open(BASE_DIR + '/temp_scholar.jsonl'))
    selInit = SeleniumInit()
    for expert, scholar in zip(experts_list, scholar_list):
        print(f"\n当前进度处理专家\n：{expert}")
        # 解析url
        selInit.page_parse(url=url)
        # 搜索专家
        query_word(scholar, selInit)
        time_sleep(1, 2)
        cur_url = selInit.browser.current_url
        print(cur_url)
        # TODO 词条未被收录，退出
        if 'none?' in cur_url:
            print(f"词条 {scholar['inventor_name']} 未被收录！")
            scholar_info_list = [{"inventor_id": scholar["inventor_id"], "inventor_name": scholar['inventor_name'], "full_name": scholar["full_name"], "short_name": scholar["short_name"], "baike_search_log": "当前词条未被收录"}]
            expert['baike_info'] = ''
            expert['baike_search_log'] = '当前词条未被收录'
            insert_data(scholar_info_list)
            continue
        # TODO 有词条收录，待匹配
        scholar_info_list = check_word(selInit, scholar)
        # TODO 百科数据向补充写入
        if 'data' in scholar:
            expert['baike_info'] = scholar['data']
            expert.pop('data', None)
            if 'base_info' in expert['baike_info']:
                table_info = expert['baike_info']['base_info']
                for info in table_info:
                    if '国籍' in info:
                        expert['nationality'] = info['国籍']
                    if '毕业院校' in info:
                        expert['graduate_university'] = info['毕业院校']
                    if '职称' in info:
                        expert['position'] = info['职称']
                    if '学历' in info:
                        expert['edu_background'] = info['学历']
                    elif '学位/学历' in info:
                        expert['edu_background'] = info['学位/学历']

            if 'intro' in expert['baike_info'] and expert['baike_info']['intro'] != '':
                expert['cv'] = expert['baike_info']['intro']
            if 'occupation' in expert['baike_info'] and expert['baike_info']['occupation'] != '':
                expert['position'] = expert['baike_info']['occupation']

            if '研究方向' in expert['baike_info'] and expert['baike_info']['研究方向'] != '':
                expert['research_field'] = expert['baike_info']['研究方向']
            elif '研究领域' in expert['baike_info'] and expert['baike_info']['研究领域'] != '':
                expert['research_field'] = expert['baike_info']['研究领域']
            elif '主要研究方向' in expert['baike_info'] and expert['baike_info']['主要研究方向'] != '':
                expert['research_field'] = expert['baike_info']['主要研究方向']

            if '个人经历' in expert['baike_info'] and expert['baike_info']['个人经历'] != '':
                expert['expert_experience'] = expert['baike_info']['个人经历']
            elif '人物经历' in expert['baike_info'] and expert['baike_info']['人物经历'] != '':
                expert['expert_experience'] = expert['baike_info']['人物经历']

            if '主要成就' in expert['baike_info'] and expert['baike_info']['主要成就'] != '':
                expert['achievements'] = expert['baike_info']['主要成就']
            elif '学术成果' in expert['baike_info'] and expert['baike_info']['学术成果'] != '':
                expert['achievements'] = expert['baike_info']['学术成果']
            elif '主要贡献' in expert['baike_info'] and expert['baike_info']['主要贡献'] != '':
                expert['achievements'] = expert['baike_info']['主要贡献']
            elif '主要成果' in expert['baike_info'] and expert['baike_info']['主要成果'] != '':
                expert['achievements'] = expert['baike_info']['主要成果']

            if '获奖记录' in expert['baike_info'] and expert['baike_info']['获奖记录'] != '':
                expert['awards'] = expert['baike_info']['获奖记录']
            elif '荣誉' in expert['baike_info'] and expert['baike_info']['荣誉'] != '':
                expert['awards'] = expert['baike_info']['荣誉']
            elif '学术兼职：' in expert['baike_info'] and expert['baike_info']['学术兼职：'] != '':
                expert['awards'] = expert['baike_info']['学术兼职：']

        insert_data(scholar_info_list)
        print(expert)
        # print('=' * 30)

    selInit.close_browser()


if __name__ == '__main__':
    baike_info_get_run([{'inventor_id': 18447, 'inventor_name': '张万舟', 'full_name': '太原理工大学', 'short_name': '太原理工大学'}])
    pass
