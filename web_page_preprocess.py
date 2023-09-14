from name_entity_reg import name_reg_hanlp
from name_entity_reg import name_reg_texsamrt
from SentenceSeparate import sentences_to_chunks
import time

def noisy_text_clean(page_content: str, tgt_name: str):
    # print(page_content)
    if isinstance(page_content, str):
        contents = page_content.split('<SEP>')
    else:
        return page_content
    contents = sentences_to_chunks(contents)
    start = time.time()
    cleaned_contents = []
    for content in contents:
        try:
            name_entitys = name_reg_hanlp(content)
        except Exception as e:
            # print("Hanlp客户端速率受限...\n切换Texmsart进行...")
            name_entitys = name_reg_texsamrt(content)
        # print(name_entitys, '\n' + '=' * 30)
        if name_entitys: #存在姓名实体
            tgt_in = False
            for name_entity in name_entitys:
                if tgt_name == name_entity:
                    tgt_in = True
                    break
            if tgt_in: #
                # print(content, '\n' + '=' * 30)
                cleaned_contents.append(content)
        else: #不存在姓名实体 无法判断 暂时保留
            # print(content, '\n' + '=' * 30)
            cleaned_contents.append(content)
    clearned_page = '<SEP>'.join(cleaned_contents)
    # print(clearned_page)
    end = time.time()
    print("\n分网页预处理耗时: {:.2f} 秒".format(end - start))
    return clearned_page