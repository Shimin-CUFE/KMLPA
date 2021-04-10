"""entropy weight method"""
import numpy as np


def ewm_weight(*inds):
    """
    通过熵权法计算指标权重
    get weight through ewm
    :param inds: 若干指标字典（注：字典key排序需保持一致）
    :return: 指标权重列表，按输入字典顺序排列
    """
    # 初始化
    a = []
    for ind in inds:
        a.append(list(ind.values()))
    a = np.array(a)
    # min-max法标准化，归一化
    a = np.apply_along_axis(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)), 1, a)
    p = a
    for i in range(p.shape[0]):
        s = np.sum(p[i])
        for j in range(p.shape[1]):
            if p[i, j] != 0 and s != 0:
                p[i, j] /= s
            else:
                p[i, j] = 0
    # 求信息熵
    h = []
    k = -(1 / np.log(p.shape[0]))
    for i in range(p.shape[0]):
        s = 0
        for j in range(p.shape[1]):
            if p[i, j] != 0:
                s += p[i, j] * np.log(p[i, j])
        h.append(s * k)
    # 计算权重
    w = []
    for value in h:
        w.append((1 - value) / (len(h) - sum(h)))
    # print(w)
    return w


if __name__ == "__main__":  # 测试熵权法
    dict1 = {1: 2, 3: 4, 5: 6, 7: 8}
    dict2 = {7: 8, 9: 10, 11: 16, 13: 14}
    dict3 = {15: 16, 17: 18, 19: 20, 21: 22}
    weight = ewm_weight(dict1, dict2, dict3)
    print("weight list: ")
    print(weight)
    print(sum(weight))
