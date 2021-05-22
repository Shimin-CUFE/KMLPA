"""Model class label propagation."""

import random
import time

from community import modularity
import networkx as nx
import numpy as np
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score

from data_tools import json_dumper, csv_dumper, plot_printer
from ewm import ewm_weight
from weight import *


class LabelPropagator:
    """
    标签传播算法类，传入networkx graph对象与参数对象进行初始化，调用label_propagation()方法进行标签传播迭代
    Label propagation class.
    """

    def __init__(self, graph, args):
        """
        初始化对象，读取参数与networkx graph对象，生成nodes与labels列表
        Setting up the Label Propagator object.
        :param graph: NetworkX object.
        :param args: Arguments object.
        """
        print("[INIT]Initialization start")
        self.graph = graph
        # 处理自接节点
        for (u, v) in self.graph.edges:
            if u == v:
                self.graph.remove_edge(u, v)
        self.nodes = [node for node in graph.nodes()]
        self.labels = {node: node for node in self.nodes}
        self.degree = dict(self.graph.degree)
        # self.degree_centrality = nx.degree_centrality(self.graph)
        self.eigenvector_centrality = nx.eigenvector_centrality(self.graph)  # 节点特征向量中心性
        # self.info_centrality = nx.information_centrality(self.graph)
        # self.per_centrality = nx.percolation_centrality(self.graph)
        # self.voterank = nx.voterank(self.graph)

        # self.community: 真实社区划分
        # 若输入为football网络：参数改为value
        # [暂时不可用]若输入为LFR benchmark network: 参数改为community
        self.community = nx.get_node_attributes(self.graph, "community")
        self.max_round = args.rounds
        self.weight_setup(args.weighting)
        print("[INIT]Initialization done\n")

    def weight_setup(self, weighting):
        """
        边权重生成方法
        Calculating the edge weights.
        :param weighting: Type of edge weights.
        """
        if weighting == "overlap":
            self.weights = weight_generator(overlap, self.graph)
        elif weighting == "unit":
            self.weights = weight_generator(unit, self.graph)
        elif weighting == "min_norm":
            self.weights = weight_generator(min_norm, self.graph)
        elif weighting == "normalized_overlap":
            self.weights = weight_generator(normalized_overlap, self.graph)
        else:
            pass

    def pre_processing(self):
        """
        预处理部分：综合K核分解与节点度数的影响力认定
        :return: None
        """
        print("[PRE]Start pre-processing")
        # K核分解部分
        # # K-shell
        # graph_replica = self.graph.copy()
        # k_dict = {node: 0 for node in self.nodes}
        # while len(graph_replica.nodes) != 0:
        #     nodes = list(graph_replica.nodes)
        #     degrees = list(dict(graph_replica.degree).values())
        #     for num in range(len(degrees)):
        #         if degrees[num] == min(degrees):
        #             graph_replica.remove_node(nodes[num])
        #             k_dict[nodes[num]] = min(degrees)

        # k_iterations字典: {node: K核迭代次数}
        graph_replica = self.graph.copy()
        k_dict = {node: 0 for node in self.nodes}
        iteration = 1
        while len(graph_replica.nodes) != 0:
            nodes = list(graph_replica.nodes)
            degrees = list(dict(graph_replica.degree).values())
            for num in range(len(degrees)):
                if degrees[num] == min(degrees):
                    graph_replica.remove_node(nodes[num])
                    k_dict[nodes[num]] = iteration
            iteration += 1

        # 更新标签字典self.labels，给部分节点赋予初始标签
        p = np.percentile(np.array(list(set(k_dict.values()))), 25)  # [模型参数A]截取标签分位数
        for node in self.nodes:
            if k_dict[node] < p:
                self.labels[node] = None

        # 使用熵权法计算影响力，倒序排序部分
        # 综合影响力包含以下维度：k核迭代次数、节点度数（度中心性）、节点特征向量中心性
        weight = ewm_weight(k_dict, self.degree, self.eigenvector_centrality)
        result = []
        length = len(self.degree)
        for i in range(length):
            inf = list(k_dict.values())[i] * weight[0] + list(self.degree.values())[i] * weight[1] + \
                  list(self.eigenvector_centrality.values())[i] * weight[2]
            result.append(inf)
        sortres = list(dict(sorted(dict(zip(self.nodes, result)).items(), key=lambda x: x[1], reverse=True)).keys())
        self.nodes = sortres
        print("[PRE]End of pre-processing")

    def post_processing(self):
        """
        后处理部分：合并孤岛社区
        :return: None
        """
        print("[POST]Start post-processing")
        label_set = list(set(self.labels.values()))
        coh = []
        # count = [0 for i in range(len(set(self.labels.values())))]
        dimout_max = dict.fromkeys(label_set, 0)
        t = 0.7  # 设定一个阈值
        merge_count = 0
        for i in range(len(set(self.labels.values()))):
            dimin = 0
            dimout = 0
            for node in self.nodes:
                if self.labels[node] == label_set[i]:
                    # count[i] += 1
                    for neighbor in self.graph.neighbors(node):
                        neighbor_label = self.labels[neighbor]
                        if neighbor_label == label_set[i]:
                            dimin += 1
                        else:
                            dimout += 1
                            dimout_max[neighbor_label] += 1
            dimin /= 2
            # print("Community-%d has %d edges, %d nodes" % (i, dimin, count[i]))
            if dimout == 0:
                coh.append(0)
                continue
            else:
                coh.append(dimin / dimout)
            if coh[i] <= t:  # 合并社区
                merge_count += 1
                for node in self.nodes:
                    if self.labels[node] != label_set[i]:
                        continue
                    else:
                        new_community = max(dimout_max, key=lambda x: dimout_max[x])
                        print("Merging node-%s at community-%s into community-%s. " % (node, self.labels[node], new_community))
                        self.labels[node] = new_community
        print("Merged %d communities. " % merge_count)
        print("[POST]End of post-processing\n")
        pass

    def pick_neighbor(self, source, neighbors):
        """
        从节点的邻居中选择一个标签
        Choosing a neighbor from a propagation source node.
        :param source: Source node.
        :param neighbors: Neighboring nodes.
        """
        scores = {self.labels[source]: 0.0}
        for neighbor in neighbors:
            neighbor_label = self.labels[neighbor]
            if neighbor_label is None:
                scores[neighbor_label] = -1.0
            else:
                scores[neighbor_label] = scores.setdefault(neighbor_label, 0.0) + self.weights[(neighbor, source)]
        scores_items = list(scores.items())
        scores_items.sort(key=lambda x: x[1], reverse=True)
        # if there is not only one label with maximum count then choose one randomly
        labels = [(k, v) for k, v in scores_items if v == scores_items[0][1]]
        label = random.sample(labels, 1)[0][0]
        return label

    def estimate_stop_cond(self):
        """
        更新一轮，查看节点标签是否继续变化，若无变化则停止迭代
        :return: 迭代指示布尔值。False-停止迭代
        """
        for node in self.nodes:
            count = {self.labels[node]: 0.0}
            for neighbor in self.graph.neighbors(node):
                neighbor_label = self.labels[neighbor]
                if neighbor_label is None:
                    count[neighbor_label] = -1.0
                else:
                    count[neighbor_label] = count.setdefault(neighbor_label, 0.0) + self.weights[(neighbor, node)]
            count_items = list(count.items())
            count_items.sort(key=lambda x: x[1], reverse=True)
            new_labels = [k for k, v in count_items if v == count_items[0][1]]
            # 停止条件：没有新的label发生变化
            if self.labels[node] not in new_labels:
                return False
        return True

    def label_propagation(self):
        """
        运行标签传播算法，直到收敛（无新标签生成）或达到迭代轮数上限
        Doing propagations until convergence or reaching round budget.
        """
        lpa_start = time.time()

        self.pre_processing()  # 预处理
        iter_round = 0
        while True:
            iter_round += 1
            print("[RUNNING]Label propagation round: %s" % str(iter_round))
            # 标签传播循环，从邻居节点中挑选标签
            for node in self.nodes:
                if self.degree[node] == 0:
                    self.labels[node] = node
                else:
                    neighbors = self.graph.neighbors(node)
                    self.labels[node] = self.pick_neighbor(node, neighbors)
            # 判断停止条件与迭代轮数
            stop_cond = self.estimate_stop_cond()
            print("[RUNNING]Round %d stop condition: %s" % (iter_round, stop_cond))
            if iter_round > self.max_round or stop_cond is True:
                break
        self.post_processing()  # 后处理

        lpa_end = time.time()
        label_count = len(set(self.labels.values()))

        # TODO: 输出社区数据
        print("[RES]%d nodes, %d edges with %d communities, %f seconds and %d rounds consumed" % (
            len(self.nodes), len(self.graph.edges), label_count, (lpa_end - lpa_start), iter_round))
        # print("Graph diameter: %d" % nx.diameter(self.graph))  # 返回图G的直径（最长最短路径的长度）
        # print("Graph average SP length: %f" % nx.average_shortest_path_length(self.graph))  # 返回图G所有节点间平均最短路径长度。
        avg_clustering = nx.average_clustering(self.graph)
        print("Graph average clustering: %f" % avg_clustering)  # 平均群聚系数
        # node_clustering = nx.clustering(self.graph)  # 节点群聚系数

        # 模块度计算 Calculate modularity
        mod = modularity(self.labels, self.graph)
        print("Modularity: %f" % mod)

        # NMI and ARI
        nmi = normalized_mutual_info_score(list(self.labels.values()), list(self.community.values()))
        print("NMI: %f" % nmi)
        ari = adjusted_rand_score(list(self.labels.values()), list(self.community.values()))
        print("ARI: %f" % ari)

        # 绘图 Draw plot
        choice = input("[PLOT]Print plot? (y/n): ")
        if choice == "y" or choice == "Y":
            plot_printer(self.graph, self.labels)

        # 输出结果
        json_dumper(self.labels)
        csv_dumper(np.array([len(self.nodes), len(self.graph.edges), label_count, (lpa_end - lpa_start), iter_round,
                             avg_clustering, mod, nmi, ari]))

        print("\n[FINISH]Finish running of Label propagation model")
