import json
import time
import requests
import random
import pandas as pd
import Levenshtein
import jsonlines
from tqdm import tqdm
from lxml import etree
import os
import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)

Agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36']

query_headers = {
    # 'Cookie': 'Ecp_ClientId=b221231132700425170; Ecp_loginuserbk=SDSFDX; Ecp_ClientIp=27.192.36.17; Ecp_loginuserjf=15065629195; refRmbUser=true; refUserName=15065629195; refPassWord=yang8302; _pk_ref=["","",1673187840,"https://expert.cnki.net/"]; Ecp_Userid=1048946546; _pk_id=5291180d-215f-4c39-bbca-13666ef1cb04.1672464434.4.1673187844.1673187840.; ASP.NET_SessionId=f2lukbrkkzpfzwrmmgmhrkbt; SID=124001; Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"15065629195","ShowName":"15065629195","UserType":"jf","BUserName":"","BShowName":"","BUserType":"","r":"VhBpu5","Members":[]}; LID=WEEvREcwSlJHSldTTEYySCtSNGRyakdnYlNKYlNCeTVjMzZzTUFtdlZ5UT0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!; c_m_LinID=LinID=WEEvREcwSlJHSldTTEYySCtSNGRyakdnYlNKYlNCeTVjMzZzTUFtdlZ5UT0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=01/09/2023 10:06:43; c_m_expire=2023-01-09 10:06:43',
    'User-Agent': random.choice(Agents),
    "Referer":"https://expert.cnki.net/Search/AdvFind",
}

info_headers = {
    'Cookie': 'Ecp_ClientId=b221231132700425170; Ecp_loginuserbk=SDSFDX; Ecp_ClientIp=27.192.36.17; Ecp_Userid=1048946546; Ecp_loginuserjf=15065629195; ASP.NET_SessionId=vfgybwropbtkcgnfzw3zgqah; SID=124007; Ecp_session=1; _pk_ref=["","",1674974040,"https://www.baidu.com/link?url=HANxraT8WS48bA0N0Rc2fSuUOSeItj39RsCBUyZWgHm&wd=&eqid=be723b0a000358a90000000263c7c8de"]; _pk_id=5291180d-215f-4c39-bbca-13666ef1cb04.1672464434.7.1674974938.1674974040.; Ecp_IpLoginFail=230129123.133.73.83; Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"15065629195","ShowName":"15065629195","UserType":"jf","BUserName":"","BShowName":"","BUserType":"","r":"lADJEK","Members":[]}; LID=WEEvREcwSlJHSldTTEYzVnBFdUNaSk9ldHFmVXJ4bEVwRDJxUUVPUjU4Zz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!; c_m_LinID=LinID=WEEvREcwSlJHSldTTEYzVnBFdUNaSk9ldHFmVXJ4bEVwRDJxUUVPUjU4Zz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=01/29/2023 17:10:35; c_m_expire=2023-01-29 17:10:35',
    'User-Agent': random.choice(Agents),
    'Referer': 'https://expert.cnki.net/Search/AdvFind',
}

cnki_prefix = 'https://expert.cnki.net/'

current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

def get_value(html,path):

    try:
        value = html.xpath(path)[0]
    except:
        value = ''

    return value

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
    # print(r)

    return r['res_list'][0]['score']

def expert_detail_query(expert_name, expert_company):

    url = 'https://expert.cnki.net/Search/AdvFindResult'

    expert_com = expert_company.strip('股份')
    expert_com = expert_com.strip('控股')
    expert_com = expert_com.strip(' Electronics')

    datas = {
        'fieldParam': '',
        'name_pcni_select': 'name_0',
        'name_0': expert_name,
        'name_match_0': 0,
        'unit_relation_0': 11,
        'unit_0': expert_com,
        'unit_match_0': 1,
        'name_relation_1': 11,
        'name_pcni_select': 'name_1',
        'name_1': '',
        'name_match_1': 0,
        'unit_relation_1': 11,
        'unit_1': '',
        'unit_match_1': 1,
        'name_relation_2': 11,
        'name_pcni_select': 'name_2',
        'name_2': '',
        'name_match_2': 0,
        'unit_relation_2': 11,
        'unit_2': '',
        'unit_match_2': 1,
        'name_relation_3': 11,
        'name_pcni_select': 'name_3',
        'name_3': '',
        'name_match_3': 0,
        'unit_relation_3': 11,
        'unit_3': '',
        'unit_match_3': 1,
        'name_relation_4': 11,
        'name_pcni_select': 'name_4',
        'name_4': '',
        'name_match_4': 0,
        'unit_relation_4': 11,
        'unit_4': '',
        'unit_match_4': 1,
        'keyword_0': '',
        'keyword_match_0': 1,
        'researcharea_relation_0': 11,
        'researcharea_0': '',
        'keyword_relation_1': 11,
        'keyword_1': '',
        'keyword_match_1': 1,
        'researcharea_relation_1': 11,
        'researcharea_1': '',
        'keyword_relation_2': 11,
        'keyword_2': '',
        'keyword_match_2': 1,
        'researcharea_relation_2': 11,
        'researcharea_2': '',
        'keyword_relation_3': 11,
        'keyword_3': '',
        'keyword_match_3': 1,
        'researcharea_relation_3': 11,
        'researcharea_3': '',
        'keyword_relation_4': 11,
        'keyword_4': '',
        'keyword_match_4': 1,
        'researcharea_relation_4': 11,
        'researcharea_4': '',
        'fund_match_0': 1,
        'fundcodes': '',
        'statNum_field_0': 9,
        'statNum_match_0': 3,
        'statNum_0': '',
        'statNum_relation_1': 11,
        'statNum_field_1': 9,
        'statNum_match_1': 3,
        'statNum_1': '',
        'statNum_relation_2': 11,
        'statNum_field_2': 9,
        'statNum_match_2': 3,
        'statNum_2': '',
        'statNum_relation_3': 11,
        'statNum_field_3': 9,
        'statNum_match_3': 3,
        'statNum_3': '',
        'statNum_relation_4': 11,
        'statNum_field_4': 9,
        'statNum_match_4': 3,
        'statNum_4': '',
        'X-Requested-With': 'XMLHttpRequest'
} #post请求 form_data
    html = ''

    try:
        resp = requests.post(url=url, headers=query_headers,data=datas)
        html = etree.HTML(resp.text)
        resp.close()
    except Exception as e:
        print(f'Error: {e}')
        return None

    mainpage_url = get_value(html,'//*[@id="findSearchPager"]/ul/li[1]//div[@class="el-link"]/span/a/@href')
    if mainpage_url == '':
        print(f'\n专家: {expert_name}-{expert_company}-全称检索失败')
        return None
    mainpage_url = cnki_prefix + mainpage_url

    return mainpage_url

def expert_detail_query2(expert_name, expert_company):

    url = 'https://expert.cnki.net/Search/AdvFindResult'

    expert_com = expert_company.strip('股份')
    expert_com = expert_com.strip('控股')
    expert_com = expert_com.strip(' Electronics')

    datas = {
        'fieldParam': '',
        'name_pcni_select': 'name_0',
        'name_0': expert_name,
        'name_match_0': 0,
        'unit_relation_0': 11,
        'unit_0': expert_com,
        'unit_match_0': 1,
        'name_relation_1': 11,
        'name_pcni_select': 'name_1',
        'name_1': '',
        'name_match_1': 0,
        'unit_relation_1': 11,
        'unit_1': '',
        'unit_match_1': 1,
        'name_relation_2': 11,
        'name_pcni_select': 'name_2',
        'name_2': '',
        'name_match_2': 0,
        'unit_relation_2': 11,
        'unit_2': '',
        'unit_match_2': 1,
        'name_relation_3': 11,
        'name_pcni_select': 'name_3',
        'name_3': '',
        'name_match_3': 0,
        'unit_relation_3': 11,
        'unit_3': '',
        'unit_match_3': 1,
        'name_relation_4': 11,
        'name_pcni_select': 'name_4',
        'name_4': '',
        'name_match_4': 0,
        'unit_relation_4': 11,
        'unit_4': '',
        'unit_match_4': 1,
        'keyword_0': '',
        'keyword_match_0': 1,
        'researcharea_relation_0': 11,
        'researcharea_0': '',
        'keyword_relation_1': 11,
        'keyword_1': '',
        'keyword_match_1': 1,
        'researcharea_relation_1': 11,
        'researcharea_1': '',
        'keyword_relation_2': 11,
        'keyword_2': '',
        'keyword_match_2': 1,
        'researcharea_relation_2': 11,
        'researcharea_2': '',
        'keyword_relation_3': 11,
        'keyword_3': '',
        'keyword_match_3': 1,
        'researcharea_relation_3': 11,
        'researcharea_3': '',
        'keyword_relation_4': 11,
        'keyword_4': '',
        'keyword_match_4': 1,
        'researcharea_relation_4': 11,
        'researcharea_4': '',
        'fund_match_0': 1,
        'fundcodes': '',
        'statNum_field_0': 9,
        'statNum_match_0': 3,
        'statNum_0': '',
        'statNum_relation_1': 11,
        'statNum_field_1': 9,
        'statNum_match_1': 3,
        'statNum_1': '',
        'statNum_relation_2': 11,
        'statNum_field_2': 9,
        'statNum_match_2': 3,
        'statNum_2': '',
        'statNum_relation_3': 11,
        'statNum_field_3': 9,
        'statNum_match_3': 3,
        'statNum_3': '',
        'statNum_relation_4': 11,
        'statNum_field_4': 9,
        'statNum_match_4': 3,
        'statNum_4': '',
        'X-Requested-With': 'XMLHttpRequest'
} #post请求 form_data
    html = ''

    try:
        resp = requests.post(url=url, headers=query_headers,data=datas)
        html = etree.HTML(resp.text)
        resp.close()
    except Exception as e:
        print(f'Error: {e}')
        return None

    mainpage_url = get_value(html,'//*[@id="findSearchPager"]/ul/li[1]//div[@class="el-link"]/span/a/@href')
    if mainpage_url == '':
        print(f'\n专家: {expert_name}-{expert_company}-简称检索失败')
        return None
    mainpage_url = cnki_prefix + mainpage_url

    return mainpage_url


def expert_detail_query3(expert_name, expert_company):
    url = 'https://expert.cnki.net/Search/AdvFindResult'

    expert_com = expert_company.strip('股份')
    expert_com = expert_com.strip('控股')
    expert_com = expert_com.strip(' Electronics')

    datas = {
        'fieldParam': '',
        'name_pcni_select': 'name_0',
        'name_0': expert_name,
        'name_match_0': 0,
        'unit_relation_0': 11,
        'unit_0': '',
        'unit_match_0': 1,
        'name_relation_1': 11,
        'name_pcni_select': 'name_1',
        'name_1': '',
        'name_match_1': 0,
        'unit_relation_1': 11,
        'unit_1': '',
        'unit_match_1': 1,
        'name_relation_2': 11,
        'name_pcni_select': 'name_2',
        'name_2': '',
        'name_match_2': 0,
        'unit_relation_2': 11,
        'unit_2': '',
        'unit_match_2': 1,
        'name_relation_3': 11,
        'name_pcni_select': 'name_3',
        'name_3': '',
        'name_match_3': 0,
        'unit_relation_3': 11,
        'unit_3': '',
        'unit_match_3': 1,
        'name_relation_4': 11,
        'name_pcni_select': 'name_4',
        'name_4': '',
        'name_match_4': 0,
        'unit_relation_4': 11,
        'unit_4': '',
        'unit_match_4': 1,
        'keyword_0': '',
        'keyword_match_0': 1,
        'researcharea_relation_0': 11,
        'researcharea_0': '',
        'keyword_relation_1': 11,
        'keyword_1': '',
        'keyword_match_1': 1,
        'researcharea_relation_1': 11,
        'researcharea_1': '',
        'keyword_relation_2': 11,
        'keyword_2': '',
        'keyword_match_2': 1,
        'researcharea_relation_2': 11,
        'researcharea_2': '',
        'keyword_relation_3': 11,
        'keyword_3': '',
        'keyword_match_3': 1,
        'researcharea_relation_3': 11,
        'researcharea_3': '',
        'keyword_relation_4': 11,
        'keyword_4': '',
        'keyword_match_4': 1,
        'researcharea_relation_4': 11,
        'researcharea_4': '',
        'fund_match_0': 1,
        'fundcodes': '',
        'statNum_field_0': 9,
        'statNum_match_0': 3,
        'statNum_0': '',
        'statNum_relation_1': 11,
        'statNum_field_1': 9,
        'statNum_match_1': 3,
        'statNum_1': '',
        'statNum_relation_2': 11,
        'statNum_field_2': 9,
        'statNum_match_2': 3,
        'statNum_2': '',
        'statNum_relation_3': 11,
        'statNum_field_3': 9,
        'statNum_match_3': 3,
        'statNum_3': '',
        'statNum_relation_4': 11,
        'statNum_field_4': 9,
        'statNum_match_4': 3,
        'statNum_4': '',
        'X-Requested-With': 'XMLHttpRequest'
    }  # post请求 form_data

    html = ''

    try:
        resp = resp = requests.post(url=url, headers=query_headers, data=datas)
        html = etree.HTML(resp.text)
        resp.close()
    except Exception as e:
        print(f'Error: {e}')
        return None

    ul_xpath = '//*[@id="findSearchPager"]/ul'
    ul_list = html.xpath(ul_xpath)

    if ul_list == []:
        return None

    link_list = []

    for ul in ul_list:
        el_list = ul.xpath('.//div[@class="el-info"]/p/text()')
        el = '' if el_list == [] else el_list[0]
        sim_rate = Levenshtein.ratio(el, expert_com)
        el = el.strip('有限公司')
        el = el.lstrip('中国')
        expert_com = expert_com.lstrip('中国')

        esim_sim, linkage_sim = texsmart_query(el, expert_com, 'esim'), texsmart_query(el, expert_com, 'linkage')
        sim = 0.5 * esim_sim + 0.5 * linkage_sim
        print(el, expert_com, esim_sim, linkage_sim)
        print('=' * 30)
        if sim > 0.35:
            link = cnki_prefix + ul.xpath('.//div[@class="el-link"]//a/@href')[0]
            link_list.append((link, sim_rate))

    if link_list == []:
        return None

    link_list.sort(key=lambda pair: pair[1], reverse=True)
    mainpage_url = link_list[0][0]

    return mainpage_url


def cnki_url_get_run(experts_list):

    write_path = BASE_DIR + f'/experts_url_{current_date}.json'

    # experts_list = []

    # with open(data_path, 'r', encoding='utf-8') as f:
    #     for line in f.readlines():
    #         data_out = json.loads(line)
    #         experts_list.append(data_out)

    for expert in experts_list:

            id, expert_name, full_name, short_name = expert['id'], expert['name'], expert['scholar_institute'], expert['simply_institute']

            info_url = {
                'id': id, 'name': expert_name, 'institute': full_name, 'simply_institute': short_name, 'url': ''
            }
            # print(info_url)

            query_result = expert_detail_query(expert_name, full_name)
            if query_result != None:
                info_url['url'] = query_result
                print(f'\n专家: {expert_name}-{full_name}-{query_result}主页地址获取成功')
            else:
                time.sleep(random.uniform(1.5, 2))

                query_result2 = expert_detail_query2(expert_name, short_name)
                if query_result2 != None:
                    info_url['url'] = query_result2
                    print(f'\n专家: {expert_name}-{short_name}-{query_result2}主页地址获取成功')
                else:
                    time.sleep(random.uniform(1.5, 2))

                    query_result3 = expert_detail_query3(expert_name, short_name)
                    if query_result3 != None:
                        info_url['url'] = query_result3
                        print(f'\n专家: {expert_name}-{short_name}-{query_result3}主页地址获取成功')
                    else:
                        print(f'\n专家: {expert_name}-{short_name}匹配检索失败')

            expert['cnki_url'] = info_url['url']

            data_in = json.dumps(info_url, ensure_ascii=False)
            with open(write_path,'a', encoding='utf-8') as f:
                f.write(data_in)
                f.write('\n')

if __name__ == '__main__':

    # cnki_url_get_run()
    pass