import pandas as pd
import numpy as np
import time
import joblib
import json
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from utls.TextEncode import text_encode
from SentenceSeparate import chunks_from_text
from name_entity_reg import name_reg_texsamrt, name_reg_hanlp


def data_rand_sampling(df):
    # 按照label分类
    df_label_0 = df[df['label'] == 0]
    df_label_1 = df[df['label'] == 1]

    # 确定你想要保留的label为0的数据量
    num_label_0_to_keep = len(df_label_1) * 2
    # 从label为0的数据中随机抽取数据
    df_label_0_sampled = df_label_0.sample(n=num_label_0_to_keep, random_state=42)
    # 将两个子集重新合并
    df_balanced = pd.concat([df_label_0_sampled, df_label_1], axis=0)
    # 重置索引
    df_balanced = df_balanced.reset_index(drop=True)

    return df_balanced

def load_data():
    train_data = pd.read_csv('../../../ExtractByGPT_Copy/Data/train_data_v3.csv', names=['content', 'label'], encoding='utf-8').astype(str)
    # print(train_data.head())
    toInt = lambda x: int(x)
    train_data['label'] = train_data['label'].apply(toInt)
    # 将四分类转化为二分类
    trans = lambda x: 0 if x == 0 else 1
    train_data['label'] = train_data['label'].apply(trans)
    train_data = data_rand_sampling(train_data) # 随机采样部分负样本 防止数据量差距过大
    # print(train_data.shape)
    return train_data
    

def train_svm_classifier(x_train, y_train, kernel='rbf', C=5):
    # parameters = {'kernel':('linear', 'rbf'), 'C':[0.1, 0.2, 0.5, 1, 5, 10], 'gamma':[0.125, 0.25, 0.5 ,1, 2, 4]}
    # svm_classifier = GridSearchCV(SVC(), parameters, scoring='f1', cv=5)
    svm_classifier = SVC(kernel=kernel, C=C, gamma='scale', verbose=True)
    # svm_classifier = joblib.load('./model/svm_rbf_v2.joblib')

    start_time = time.time()
    svm_classifier.fit(x_train, y_train)
    end_time = time.time()
    duration = end_time - start_time
    print("\nSVM训练耗时: {:.2f} 秒".format(duration))
    
    
    # print('The parameters of the best model are: ')
    # print(svm_classifier.best_params_)
    # print(svm_classifier.get_params)

    return svm_classifier


def evaluate_classifier(classifier, x_test, y_test):
    y_pred = classifier.predict(x_test)
    print("Confusion Matrix:")
    print(metrics.confusion_matrix(y_test, y_pred))
    print("Classification Report:")
    print(metrics.classification_report(y_test, y_pred))
    print("Accuracy Score: {:.2f}%".format(metrics.accuracy_score(y_test, y_pred) * 100))


def run():
    dataset = load_data()
    x_train, x_test, y_train, y_test = train_test_split(dataset['content'], dataset['label'], test_size=0.3)

    x_train_embeddings = text_encode(x_train.values)
    x_test_embeddings = text_encode(x_test.values)
    y_train = np.array(y_train.values)
    y_test = np.array(y_test.values)

    svm_classifier = train_svm_classifier(x_train_embeddings, y_train)
    # 保存模型
    # joblib.dump(svm_classifier, './model/svm_search_best.joblib')
    # svm_classifier = joblib.load('./model/svm_rbf_v2.joblib')
    evaluate_classifier(svm_classifier, x_test_embeddings, y_test)

def text_filter(info):
    text = info['content']
    expert_name = info["expert_name"]
    text_chunks = chunks_from_text(text)
    contents, predict = [], []
    filtered_text = ''

    clf = joblib.load('./model/svm_rbf_v2.joblib')

    for chunk in text_chunks:     
        embedding = text_encode(chunk).reshape(1, -1)
        pred = clf.predict(embedding)
        if pred[0]:
            is_name_in = False
            start = time.time()
            try:
                name_list = name_reg_hanlp(chunk)
            except Exception as e:
                print("Hanlp客户端速率受限...\n切换Texmsart进行...")
                name_list = name_reg_texsamrt(chunk)
            end = time.time()
            print("\n实体识别耗时: {:.2f} 秒".format(end - start))
            print(name_list)
            if not name_list:
                filtered_text += chunk
            else:
                for name in name_list:
                    if name == expert_name:
                        is_name_in = True
                        break
                if is_name_in:
                    filtered_text += chunk
        contents.append(chunk)
        predict.append(pred[0])
    
    # 保存本次预测数据
    # save_df = pd.DataFrame()
    # save_df['原文本'] = contents
    # save_df['抽取内容'] = predict
    # save_df.to_csv('./Data/test_data_misattr_v2.csv', mode='a', header=True, index=False, encoding='utf-8')
    # with open('./Data/test_data_v2.json', 'a', encoding='utf-8') as f:
    #     f.write(json.dumps({'原文本': info['content'].replace('<br>', ' '), '抽取内容': filtered_text}, ensure_ascii=False))
    #     f.write('\n')
    return filtered_text
        

if __name__ == '__main__':
    # run()
    # load_data()
    pass
