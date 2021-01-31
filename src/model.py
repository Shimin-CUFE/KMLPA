"""Model class label propagation."""
# 需要scipy库 Require scipy

import random
import time

import community as community_louvain
from texttable import Texttable
from tqdm import tqdm
import numpy as np

from data_tools import json_dumper, plot_printer
from ewm import ewm_weight
from modularity_calculator import modularity
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
        print("[INIT]Initialize start")
        self.args = args
        self.graph = graph
        self.nodes = [node for node in graph.nodes()]
        self.labels = {node: node for node in self.nodes}
        self.degree = dict(self.graph.degree)
        self.max_round = args.rounds
        self.weight_setup(args.weighting)
        print("[INIT]Initialize done\n")

    def weight_setup(self, weighting):
        """
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
        预处理部分
        :return: None
        """
        print("[PRE]Start pre processing")
        # K核分解部分
        # Kshell字典:{node:K-shell值}
        """
        graphReplica = self.graph.copy()
        Kshell = {node: 0 for node in self.nodes}
        while len(graphReplica.nodes) != 0:
            Nodes = list(graphReplica.nodes)
            Degrees = list(dict(graphReplica.degree).values())
            for num in range(len(Degrees)):
                if Degrees[num] == min(Degrees):
                    graphReplica.remove_node(Nodes[num])
                    Kshell[Nodes[num]] = min(Degrees)
        """

        # KIterations字典:{node:K核迭代次数}
        graphReplica = self.graph.copy()
        KIterations = {node: 0 for node in self.nodes}
        iteration = 1
        while len(graphReplica.nodes) != 0:
            Nodes = list(graphReplica.nodes)
            Degrees = list(dict(graphReplica.degree).values())
            for num in range(len(Degrees)):
                if Degrees[num] == min(Degrees):
                    graphReplica.remove_node(Nodes[num])
                    KIterations[Nodes[num]] = iteration
            iteration = iteration + 1
        # # debug
        # print(KIterations)
        # print(self.degree)

        # 更新标签字典self.labels
        average = sum(self.labels.values()) / len(self.nodes)  # 平均数
        a = np.array(list(self.labels.values()))
        p = np.percentile(a, 50)  # return 50th percentile, e.g median
        for node in self.nodes:
            if self.labels[node] < average:
                self.labels[node] = None
        print(self.labels)

        # 使用熵权法计算影响力，倒序排序部分
        # KIterations字典：{node:K核迭代次数}
        weight = ewm_weight(KIterations, self.degree)
        result = []
        length = len(self.degree)
        for i in range(length):
            inf = list(KIterations.values())[i] * weight[0] + list(self.degree.values())[i] * weight[1]
            result.append(inf)
        sortres = list(dict(sorted(dict(zip(self.nodes, result)).items(), key=lambda x: x[1], reverse=True)).keys())
        # # debug
        # print(sortres)
        self.nodes = sortres
        print("[PRE]End of pre processing")

    def post_processing(self):
        """
        后处理部分
        :return: None
        """
        print("[POST]Start post processing")

        print("[POST]End of post processing")
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
            # 停止条件：没有新的label变化
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
                neighbors = self.graph.neighbors(node)
                self.labels[node] = self.pick_neighbor(node, neighbors)
            # 判断停止条件与迭代轮数
            stop_cond = self.estimate_stop_cond()
            print("[RUNNING]Round %d stop condition: %s\n" % (iter_round, stop_cond))
            if iter_round > self.max_round or stop_cond is True:
                break
        # TODO for Chenlan

        self.post_processing(self, )  # 后处理

        lpa_end = time.time()
        label_count = len(set(self.labels.values()))
        print("[END]%d nodes with %d communities, %f seconds consumed" % (len(self.nodes), label_count, (lpa_end - lpa_start)))

        # 模块度计算 Calculate modularity
        print("[MOD]Modularity is " + str(community_louvain.modularity(self.labels, self.graph)))
        # print(modularity(self.graph, self.labels)) # 循环计算法较慢，弃用

        # # TODO
        # # 输出社区数据
        # t = Texttable()
        # t.set_deco(Texttable.HEADER)
        # t.add_rows([["Community", "Nodes", "Edges", ]])

        # 绘图 Draw plot
        choice = input("[PLOT]Print plot? (y/n): ")
        if choice == "y" or choice == "Y":
            plot_printer(self.graph, self.labels)

        # 输出结果至JSON文件 Dump result
        json_dumper(self.labels, self.args.assignment_output)

        print("[FINISH]Finish running of Label propagation model")
