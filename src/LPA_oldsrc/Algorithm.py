import random

import networkx as nx
import pandas as pd
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score
import community as community_louvain


def read_graph_from_file(path):
    if path.endswith(".csv"):
        edges = pd.read_csv(path)
        graph = nx.from_edgelist(edges.values.tolist())
    elif path.endswith(".gml"):
        graph = nx.read_gml(path, label=None)
    else:
        graph = nx.Graph(nx.LFR_benchmark_graph(1000, 2, 2, 0.2, average_degree=10, max_degree=50))
    return graph


if __name__ == '__main__':
    g = read_graph_from_file(r'D:\Study\Python\Workspace\LPA\data\adjnoun.gml')
    real_community = nx.get_node_attributes(g, "value")  # LFR: community
    gen_community = real_community.copy()
    com_count = 1
    for c in nx.algorithms.community.label_propagation_communities(g):
        for item in c:
            gen_community[item] = com_count
        com_count += 1
    mod = community_louvain.modularity(gen_community, g)
    print("Modularity: %f" % mod)
    print(normalized_mutual_info_score(list(gen_community.values()), list(real_community.values())))
    print(adjusted_rand_score(list(gen_community.values()), list(real_community.values())))
