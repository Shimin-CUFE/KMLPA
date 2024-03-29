"""Tools for data reading and writing."""

import json
import random
import time

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from texttable import Texttable
from networkx.generators.community import LFR_benchmark_graph

t = time.strftime("%Y%m%d-%H%M%S", time.localtime())


def argument_printer(args):
    """
    打印参数
    Function to print the arguments in a nice tabular format.
    :param args: Parameters used for the model.
    """
    args = vars(args)
    keys = sorted(args.keys())
    t = Texttable()
    t.add_rows([["Parameter", "Value"]])
    t.add_rows([[k.replace("_", " ").capitalize(), args[k]] for k in keys])
    print(t.draw())


def graph_reader(input_path):
    """
    从参数路径读取数据，生成图
    若路径结尾不为有效扩展名，则调用LFR benchmark network
    Function to read graph from input path.
    :param input_path: Graph read into memory.
    :return graph: Networkx graph.
    """
    if input_path.endswith(".csv"):
        edges = pd.read_csv(input_path)
        graph = nx.from_edgelist(edges.values.tolist())
    elif input_path.endswith(".gml"):
        graph = nx.read_gml(input_path, label=None)
    else:
        graph = nx.Graph(LFR_benchmark_graph(250, 3, 1.5, 0.2, average_degree=8, max_degree=50, min_community=10,
                                             max_community=50, seed=10))
    return graph


def json_dumper(data):
    """
    保存社区划分数据至JSON文件
    Function to save a JSON to disk.
    :param data: Dictionary of cluster memberships.
    :param path: Path for dumping the JSON.
    """
    with open("..\\output\\json\\" + t + "_json.json", 'w') as outfile:
        json.dump(data, outfile)


def csv_dumper(data):
    """
    保存网络数据至CSV文件
    :param data: 指标列表
    :param path: 保存路径
    """
    pd_data = pd.DataFrame(data).transpose()
    t = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    pd_data.to_csv("..\\output\\csv\\" + t + "_csv.csv")


def plot_printer(graph, labels):
    """
    使用matplotlib.pyplot进行绘图，可选择保存或显示图像
    Function to save a png file of graph plot to disk.
    :param graph: Graph to print.
    :param labels: Labels of Nodes
    """
    # # 设置参数：图片大小与颜色
    width = 30
    height = 20
    dpi = 150
    plt.figure(figsize=(width, height), dpi=dpi)

    # 绘图：分别绘制节点-边-标签
    # cmap = cm.get_cmap('viridis', (len(labels.values()) + 1))
    layout = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, layout, labels.keys(), node_size=35,
                           node_color=list(pd.Series(labels.values()).astype('category').cat.codes.values))
    nx.draw_networkx_edges(graph, layout, width=1, alpha=0.4)
    new_labels = {}
    for key in labels:
        merge_label = str(key) + "@" + str(labels[key])
        new_labels.update({key: merge_label})
    # nx.draw_networkx_labels(graph, layout, new_labels, font_size=8, font_color="r", font_weight="bold")
    # 导出：选择立即显示（show）或保存（savefig）
    plt.show()
    # plt.savefig("..\\output\\images\\" + t + "_figure.png")
    # plt.close()
