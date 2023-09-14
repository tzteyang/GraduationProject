import jsonlines

experts_list = list(jsonlines.open('./Data/res_04_28.jsonl'))
count = 0
for expert in experts_list:
    main_info = 0
    
    check = lambda x: 0 if x == [] or x == None else 1

    if 'graduate_university' in expert:
        main_info |= check(expert['graduate_university'])
    if 'scholar_history' in expert:
        main_info |= check(expert['scholar_history'])
    if 'scholar_brief_info' in expert:
        main_info |= check(expert['scholar_brief_info'])
    if 'major_achievement_list' in expert:
        main_info |= check(expert['major_achievement_list'])
    
    expert['main_info'] = main_info
    if main_info == 0:
        count += 1

print(count)
