import jsonlines
import json

# experts_list = []
# with open('Data/gpt_extract_res_0428.json', 'r', encoding='utf-8') as f:
#     for line in f.readlines():
#         experts_list.append(json.loads(line))


# for expert in experts_list:
#     if "graduate_university" in expert and isinstance(expert["graduate_university"], list):
#         info_str = ""
#         isGPT = False
#         for elem in expert["graduate_university"]:
#             if isinstance(elem, dict):
#                 info_str += elem["university"] + '|' + elem["degree"] + '|' + elem["duration"] + ';'
#             else:
#                 info_str += elem + ';'
#         if not isGPT:
#             expert["graduate_university"] = info_str
#     if "scholar_history" in expert and isinstance(expert["scholar_history"], list):
#         info_str = ""
#         isGPT = False
#         for elem in expert["scholar_history"]:
#             if isinstance(elem, dict):
#                 if not "tag" in elem:
#                     info_str += elem["position"] + '|' + elem["company"] + '|' + elem["duration"] + '|' + elem["address"] + ';'
#                 else:
#                     isGPT = True
#             else:
#                 info_str += elem + ';'
#         if not isGPT:
#             expert["scholar_history"] = info_str
#     if "major_achievement_list" in expert and isinstance(expert["major_achievement_list"], list):
#         info_str = ""
#         isGPT = False
#         for elem in expert["major_achievement_list"]:
#             if isinstance(elem, str):
#                 info_str += elem + ';'
#             else:
#                 isGPT = True
#         if not isGPT:
#             expert["major_achievement_list"] = info_str
#         # print(expert, '\n' + '=' * 20)
#     if "scholar_title" in expert and isinstance(expert["scholar_title"], list):
#         info_str = ""
#         isGPT = False
#         for elem in expert["scholar_title"]:
#             if isinstance(elem, str):
#                 info_str += elem + ';'
#             else:
#                 isGPT = True
#         if not isGPT:
#             expert["scholar_title"] = info_str
#     if "scholar_brief_info" in expert and isinstance(expert["scholar_brief_info"], list):
#         info_str = ""
#         isGPT = False
#         for elem in expert["scholar_brief_info"]:
#             if isinstance(elem, str):
#                 info_str += elem + ';'
#             else:
#                 isGPT = True
#         if not isGPT:
#             expert["scholar_brief_info"] = info_str
#     if "field" in expert and isinstance(expert["field"], list):
#         info_str = ""
#         isGPT = False
#         for elem in expert["field"]:
#             if isinstance(elem, str):
#                 info_str += elem + ';'
#             else:
#                 isGPT = True
#         if not isGPT:
#             expert["field"] = info_str



# for expert in experts_list:
#     for key in expert.keys():
#         if "source" in key:
#             info_str = ""
#             if isinstance(expert[key], list):
#                 for elem in expert[key]:
#                     info_str += elem + ';'
#             expert[key] = info_str

#     with jsonlines.open('Data/res_04_28_format.jsonl', 'a') as f:
#         f.write(expert)

experts_list = list(jsonlines.open('../../../ExtractByGPT_Copy/Data/res_04_28_format.jsonl'))

for expert in experts_list:
    for key in expert.keys():
        if isinstance(expert[key], list):
            # print(key, '\n' + '=' * 20, expert[key])
            print(expert[key])