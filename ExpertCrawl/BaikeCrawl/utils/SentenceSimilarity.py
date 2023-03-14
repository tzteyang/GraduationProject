# -*- coding:utf-8 -*-
import openai
import sys
import json
import time

def get_key():
    return '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'

def prompt_pretreatment(query: str,candidates: list):

    similarity_prompt = "我将向你提供一个查询语句和一个候选语句列表，请你从语义相似和内容相似两个方面综合考虑选出候选语句中与查询语句最为匹配的候选项。\n" \
                        "请将你的输出格式调整为: {\"code\": \"succ\", \"sentence\": \"你选择的匹配语句\"}，如果候选语句中没有可以匹配的项，则将输出格式调整为: {\"code\": \"fail\", \"sentence\": \"\"}。\n" \
                        "注意: 请不要输出除我要求格式以外的任何其他信息。请你输出候选语句中成功匹配的候选项时，不要对候选项本身的内容做任何改动。\n" \
                        "查询语句: {q}。\n" \
                        "候选语句: {c}。"

    similarity_prompt = similarity_prompt.replace("{q}", f"\"{query}\"")
    candidates_list = str(candidates).replace('[','')
    candidates_list = candidates_list.replace(']','')
    similarity_prompt = similarity_prompt.replace("{c}", candidates_list)
    
    if len(similarity_prompt) > 3200:
        similarity_prompt = similarity_prompt[:3200]
    
    return similarity_prompt


def openai_query(content, apikey):
    time.sleep(2)
    openai.api_key = apikey
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # gpt-3.5-turbo-0301
        messages=[
            {"role": "user", "content": content}
        ],
        temperature=0.2, # 控制生成的随机性 0-1越高随机性越强
        max_tokens=128, # 生成内容的最大token限制
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    print(response)
    return response.choices[0].message.content

if __name__ == '__main__':
    pass
    list = ['中国科学技术大学教授','江西赣锋锂业股份有限公司董事长，民建江西省委副主委','四川省巴中市人民检察院党组成员、副检察长','四川省凉山州教育和体育局党组成员、副局长','上海市大学优秀毕业生','同济大学教授','上海交通大学医学院附属瑞金医院人员','无锡市惠山区洛社镇信息物流园区管理办公室副主任','B612 咔叽市场副总裁']

    prompt = prompt_pretreatment("江西赣锋锂业股份有限公司", list)

    start = time.perf_counter()