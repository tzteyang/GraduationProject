import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
# 当前项目路径获取
BASE_DIR = str(Path(__file__).resolve().parent)
sys.path.append(BASE_DIR)
MODEL_SAVE_PATH = BASE_DIR + '/model'

print('sentence_transformer本地模型加载中......')
model = SentenceTransformer(
    'uer/sbert-base-chinese-nli',
    cache_folder=MODEL_SAVE_PATH
)
print('sentence_transformer本地模型完成')
print("Max Sequence Length:", model.max_seq_length)


def top5_sim_sentence(query: str, candidates: list):
    """
        借助开源模型 评估与当前语句相似度最高的top5项
    """
    results = []
    q_embedding = model.encode([query], convert_to_tensor=True)
    candidates_embeddings = model.encode(candidates, convert_to_tensor=True)
    for candidate, candidate_embedding in zip(candidates, candidates_embeddings):
        # print(q_embedding, candidate)
        cos_score = util.cos_sim(q_embedding, candidate_embedding)
        results.append((candidate, cos_score.item()))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:min(len(results), 5)]


# print(top5_sim_sentence('江西赣锋锂业股份有限公司', ['中国科学技术大学教授', '江西赣锋锂业股份有限公司董事长，民建江西省委副', '四川省巴中市人民检察院党组成员、副检察长', '四川省凉山州教育和体育局党组成员、副局长']))