"""Tools for data reading and writing."""

import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
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
    for node, data in graph.nodes(True):
        data['label'] = node
    return graph


def json_dumper(data, path):
    """
    Function to save a JSON to disk.
    :param data: Dictionary of cluster memberships.
    :param path: Path for dumping the JSON.
    """
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def plot_printer(graph, layout, nodes, labels):
    """
    Function to save a png file of network to disk.
    :param layout: Dictionary of cluster memberships.
    :param graph: Path for dumping the JSON.
    :param nodes: Nodes
    :param labels: Labels of Nodes
    """
    width = 30
    height = 20
    dpi = 72
    node_color = [float(labels[node]) for node in nodes]
    plt.figure(dpi=dpi, figsize=(width, height))
    nx.draw_networkx(graph, pos=layout, node_color=node_color, width=0.1, font_size=5, node_size=150)
    # plt.show()
    plt.savefig("..\\output\\final.png")
