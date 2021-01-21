"""entropy weight method"""
import numpy as np


def ewm_weight(*inds):
    # 从可变长参数（字典）初始化
    a = []
    for ind in inds:
        a.append(list(ind.values()))
    a = np.array(a)
    # min-max标准化
    a = np.apply_along_axis(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)), 1, a)
    print(a)
    # 求信息熵
    p = a
    for i in range(p.shape[0]):
        s = np.sum(p[i])
        for j in range(p.shape[1]):
            if p[i, j] != 0 and s != 0:
                p[i, j] /= s
            else:
                p[i, j] = 0
    print(p)
    h = []
    k = -(1 / np.log(p.shape[0]))
    for i in range(p.shape[0]):
        s = 0
        for j in range(p.shape[1]):
            if p[i, j] != 0:
                s += p[i, j] * np.log(p[i, j])
        h.append(s * k)
    print(h)
    w = []
    for value in h:
        w.append((1 - value) / (len(h) - sum(h)))
    print(w)
    return w


if __name__ == "__main__":
    dict1 = {1: 2, 3: 4, 5: 6, 7: 8}
    dict2 = {7: 8, 9: 10, 11: 16, 13: 14}
    w = ewm_weight(dict1, dict2)
    print("weight: ")
    print(w)
    print(sum(w))
