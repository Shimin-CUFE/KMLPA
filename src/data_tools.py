"""Tools for data reading and writing."""

import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from texttable import Texttable


def argument_printer(args):
    """
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
    Function to read graph from input path.
    :param input_path: Graph read into memory.
    :return graph: Networkx graph.
    """
    edges = pd.read_csv(input_path)
    graph = nx.from_edgelist(edges.values.tolist())
    # for node, data in graph.nodes(True):
    #     data['label'] = node
    return graph


def json_dumper(data, path):
    """
    Function to save a JSON to disk.
    :param data: Dictionary of cluster memberships.
    :param path: Path for dumping the JSON.
    """
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def plot_printer(graph, labels):
    """
    Function to save a png file of graph plot to disk.
    :param graph: Graph to print.
    :param labels: Labels of Nodes
    """
    # # 设置参数：图片大小与颜色
    # width = 30
    # height = 20
    # dpi = 150
    # plt.figure(figsize=(width, height), dpi=dpi)
    cmap = cm.get_cmap('viridis', max(labels.values()) + 1)
    # 绘图：分别绘制节点-边-标签
    layout = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, layout, labels.keys(), node_size=180,
                           cmap=cmap, node_color=list(labels.values()))
    nx.draw_networkx_edges(graph, layout, alpha=0.5)
    new_labels = {}
    for key in labels:
        merge_label = str(key) + "@" + str(labels[key])
        new_labels.update({key: merge_label})
    nx.draw_networkx_labels(graph, layout, new_labels, font_size=5, font_color="r", font_weight="bold")
    # 导出：选择立即显示（show）或保存（savefig）
    plt.show()
    # plt.savefig("..\\output\\final.png")
