from pyhanlp import HanLP
import re


def hanlp_segment(sentence):
    """分词(去除括号)"""
    sentence = re.sub(r'[(（].*?[)）]', '', sentence)
    words = [str(item) for item in HanLP.segment(sentence)]
    words = [item.split('/') for item in words]
    return words


def get_short_name(name):
    words = hanlp_segment(name)
    short = ''
    for i, word in enumerate(words):
        c, pos = word[0], word[1]
        flag = True
        if pos == 'core' or pos == 'w' or pos == 'ns' or pos == 'nis':
            flag = False
        if (pos == 'ns' and i > 1):
            flag = True  # 修复简称词被识别为地名
        if c == '市' and words[i - 1][1] == 'ns':
            flag = False  # 修复'市'
        if (c == '分公司' and i == len(words) - 1) or c == '实业':
            flag = True  # 修复'分公司'和'实业'
        if '有限公司' in c:
            c = c.replace('有限公司', '')
        if flag:
            short += c
    return short

# print(get_short_name('苏州达力客自动化科技有限公司'), get_short_name('苏州安洁科技股份有限公司'))
