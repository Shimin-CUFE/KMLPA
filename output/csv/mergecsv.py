import pandas as pd
import os

# 根据需要修改以下部分
path = os.path.dirname(os.path.abspath(__file__))  # 文件夹路径
filename_extenstion = '.csv'  # 文件后缀
new_file_name = 'merged_data.csv'  # 合并后的文件名
cols_new_name = ['nodes', 'edges', 'communities', 'times', 'round', 'avg_clustering', 'modularity', 'NMI', 'ARI']  # 汇总后的列名，根据需要修改
cols_num = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # 需要合并的列的索引，从0开始
file_allname = []  # 用于存储全部文件的名字
for filename in os.listdir(path):
    if os.path.splitext(filename)[1] == filename_extenstion and filename != new_file_name:  # 按.csv后缀匹配
        t = os.path.splitext(filename)[0]
        file_allname.append(t + filename_extenstion)  # 拼接.csv后缀，生成完整文件名

df = pd.DataFrame(cols_new_name).T
try:
    print('开始合并：')
    df.to_csv(path + '/' + new_file_name, encoding='utf-8', header=False, index=False)
    for fn in file_allname:
        data = pd.read_csv(path + '/' + fn)
        print('合并' + fn)
        data = data.iloc[:, cols_num]  # 跳过标题行
        print(data)
        data.to_csv(path + '/' + new_file_name, mode='a', encoding='gbk', header=False, index=False)
    print('合并结束，生成新文件：' + new_file_name)
except PermissionError as e:
    print('出现异常:' + str(type(e)) + '！\n文件已打开？请先关闭')
