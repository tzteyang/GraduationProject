import numpy as np


def scale_function(data_dict, lower_bound=40.0, upper_bound=90.0, decimal_places=3):
    """
        将PageRank迭代后处于0-1范围内且数据间数值差值过大的元素处理到40 - 90评分区间
        不改变大小次序，且对数值间的差值做平滑处理
    return: 处理后的向量
    """
    # 从字典中提取键和值
    keys = list(data_dict.keys())
    values = np.array(list(data_dict.values()))

    # 计算最小值和最大值
    min_val = np.min(values)
    max_val = np.max(values)

    # 归一化处理
    normalized_values = (values - min_val) / (max_val - min_val)

    # 转换为对数值 数值平滑
    log_values = np.log(normalized_values + 1)

    # 计算对数值的最小值和最大值
    # print(log_values)
    log_min = np.min(log_values)
    log_max = np.max(log_values)

    # 归一化处理 防止除零
    if abs(log_max - log_min < 1e-6):
        normalized_log_values = 1
    else:
        normalized_log_values = (log_values - log_min) / (log_max - log_min)

    # 缩放到指定范围内
    scaled_values = lower_bound + normalized_log_values * (upper_bound - lower_bound)

    # 对最终结果进行四舍五入，以获得指定小数位数的值
    rounded_scaled_values = np.round(scaled_values, decimals=decimal_places)

    # 将处理后的数值重新映射到字典的键
    scaled_data_dict = {key: value for key, value in zip(keys, rounded_scaled_values)}

    return scaled_data_dict
