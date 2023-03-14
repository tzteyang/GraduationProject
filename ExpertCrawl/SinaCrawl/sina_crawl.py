import json
import time
import requests
import random
import pandas as pd
from lxml import etree
from tqdm import tqdm
import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

def get_value(html,path):

    try:
        value = html.xpath(path)[0]
    except:
        value = ''

    return value

def executives_info_crawl(company, url, stockid): #获取人员简历页

    sina_prefix = 'https://vip.stock.finance.sina.com.cn/'
    date = '2022-06-18'

    html = ''

    try:
        resp = requests.get(url=url, headers=headers)
        html = etree.HTML(resp.text)
        resp.close()
    except Exception as e:
        print(f'Error: {e}')
        return None

    table_xpath = '//*[@id="comInfo1"]'

    tables = html.xpath(table_xpath)

    info_dict = {}

    for index, table in enumerate(tables):

        position_list, end_list = table.xpath('.//tr/td[2]/div/text()'), table.xpath('.//tr/td[4]/div/text()')
        name_list, url_list = table.xpath('.//tr/td[@class="ccl"]//a/text()'), table.xpath('.//tr/td[@class="ccl"]//a/@href')

        for name, url ,position, end in zip(name_list, url_list, position_list, end_list):

            if end < date and end != '--':
                continue
            if name in info_dict:
                info_dict[name]['position'] += f';{position}'
            else:
                info_dict[name] = {'com_stock': stockid}
                info_dict[name]['position'], info_dict[name]['url'] = position, sina_prefix + url

    info_list = []

    for key, value in info_dict.items():
        # print(key, value)
        temp_dict = value
        temp_dict['name'] = key
        info_list.append(temp_dict)

    return info_list


def cv_info_crawl(company, stockid):

    url = f'https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpManager/stockid/{stockid}.phtml'

    info_list = executives_info_crawl(company, url, stockid)

    if info_list == []:
        print(f'公司: {company} 获取人员简历主页失败')
        return

    time.sleep(random.uniform(2, 2.5))

    # df = pd.DataFrame.from_dict(info_dict, orient='index', columns = ['company','position','url','gender','edu_background','nationality','cv'])
    # df = df.fillna(value='')

    for info in info_list:

        name, info_url = info['name'], info['url']

        html = ''

        try:
            resp = requests.get(url=info_url, headers=headers)
            html = etree.HTML(resp.text)
            # print(type(html))
            resp.close()
        except Exception as e:
            print(f'Error: {e}')

        info['gender'] = get_value(html,'//*[@id="Table1"]/tbody/tr[1]/td[2]/div/text()')
        info['edu_background'] = get_value(html,'//*[@id="Table1"]/tbody/tr[1]/td[4]/div/text()')
        info['nationality'] = get_value(html,'//*[@id="Table1"]/tbody/tr[1]/td[5]/div/text()')
        info['cv'] = get_value(html,'//*[@id="Table1"]/tbody/tr[2]/td[2]/text()').strip()

        data_in = json.dumps(info, ensure_ascii=False)
        with open(BASE_DIR + '/experts_sina_info.json', 'a', encoding='utf-8') as f:
            f.write(data_in)
            f.write('\n')

def sina_experts_crawl_run():

    name_list = []

    with open('../ShenwanClassification/ClassificationName.txt','r',encoding='utf-8') as f:
        for line in f.readlines():
            name_list.append(line.strip('\n'))

    for sheet_name in name_list[10:]:
        file_path = f'../ShenwanClassification/{sheet_name}分类表.xlsx'

        df = pd.read_excel(file_path, converters={u'股票代码': str})
        # if sheet_name == '计算机':
            # df = df[314:]
        print(f'当前正在读取: {sheet_name}分类表\n' + '=' * 30)
        print(df.head())

        for row in tqdm(df.itertuples(), total=df.shape[0]):
            industry, stockid, company = row[1], row[2], row[3]
            cv_info_crawl(company, stockid)
            time.sleep(random.uniform(2, 2.5))


if __name__ == '__main__':

    sina_experts_crawl_run()


