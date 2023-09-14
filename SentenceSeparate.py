import spacy
import jsonlines
import jieba
import jieba.analyse as analyse
import jieba.posseg as posseg
import pandas as pd
from tqdm import tqdm


def sentences_to_chunks(sentences: list):
    """
        将按句子粒度分割的文本列表
        重组为长度250<= len <= 300的文本chunk列表

        在此模块调整chunk的size
    """
    cur_len = 0
    next_index = 0
    cur_chunk = ''
    total = len(sentences)
    chunks = []
    while next_index < total:
        while next_index < total and cur_len <= 250:
            cur_len += len(sentences[next_index])  
            cur_chunk += sentences[next_index] 
            next_index += 1
        chunks.append(cur_chunk)
        cur_chunk = ''
        cur_len = 0
    recut_chunks = []
    for chunk in chunks:
        chunk_size = len(chunk)
        for i in range(0, chunk_size, 300 - 15):
            recut_chunks.append(chunk[i:(i + 300)])
    return recut_chunks
    

def chunks_from_text(text):
    """
        从传入的文本网页中获取文本chunk
    """
    text_chunks = []
    nlp = spacy.load("zh_core_web_sm")
    try:
        doc = nlp(text)
        separated_texts = [sent.text.replace('<SEP>', ' ') for sent in doc.sents]

        text_chunks = sentences_to_chunks(separated_texts)
    except Exception as e:
        print('当前网页文本分局错误或请求超时:\n', str(e))

    return text_chunks


def sentenceChunks_to_csv(text_chunks):
    """
        将文本chunk存入csv文件
    """
    columns = ['content', 'label']
    labels = [0 for i in range(len(text_chunks))]

    save_df = pd.DataFrame(data=list(zip(text_chunks, labels)))

    save_df.to_csv('./Data/train_data_v3.csv', mode='a', header=False, index=False, encoding='utf-8')


def read_stop_words():
    """
        加载停用词列表
    """
    with open('./StopWords.txt', 'r', encoding='utf-8') as f:
        stop_words = [line.strip() for line in f.readlines()]
    return stop_words


def clean_chunks(text_chunks):
    """
        对每个chunk分词后去除停用词返回
    """
    stop_words = read_stop_words()
    cleaned_chunks = []

    for chunk in text_chunks:
        cleaned_text = '' 
        word_list = list(jieba.cut(chunk.strip()))
        for word in word_list:
            if word not in stop_words and word != '\t':
                cleaned_text += word + ' '
        cleaned_chunks.append(cleaned_text)
        # print('原文本: \n', chunk, '\n' + '='*30 + '\n', '去除停用词后: \n',cleaned_text)

    return cleaned_chunks

# def separate_run(info):
#     text = info['content']
#     text_chunks = chunks_from_text(text)
#     contents, probabilitys = [], []
#     separated_text = ''
#     for chunk in text_chunks:     
#         # print('原文本: \n', chunk,len(chunk))
#         cut_chunk = clean_chunks([chunk])
#         # print('分块后文本: \n', cut_chunk, len(cut_chunk))
#         pred = chunk_check(cut_chunk)      
#         contents.append(cut_chunk)
#         probabilitys.append(pred)
#         if pred >= 0.5:
#             separated_text += chunk
#     print(separated_text,'\n' + '=' * 30)
    # 保存本次预测数据
    # columns = ['content', 'probability']
    # save_df = pd.DataFrame(data=list(zip(contents, probabilitys)))
    # save_df.to_csv('./Data/test_data_v1.csv', mode='a', header=False, index=False, encoding='utf-8')


def dataset_gen():
    """
        生成训练数据
    """
    json_list = list(jsonlines.open('./res.jsonl'))[-50:]
    text_list = [json['content'] for json in json_list]

    # texts = []
    for text in tqdm(text_list):
        # print(text,'\n', '='*30)
        text_chunks = chunks_from_text(text)
        # print(text_chunks, '\n', '='*30)
        # text_chunks = clean_chunks(text_chunks)

        sentenceChunks_to_csv(text_chunks)


if __name__ == '__main__':
    pass
    # dataset_gen()
    