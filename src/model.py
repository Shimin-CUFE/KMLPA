"""Model class label propagation."""

import random
import networkx as nx
from tqdm import tqdm
from calculation_helper import overlap, unit, min_norm, normalized_overlap, overlap_generator
from print_and_read import json_dumper
import matplotlib.pyplot as plt
# need library scipy


class LabelPropagator:
    """
    Label propagation class.
    """

    def __init__(self, graph, args):
        """
        Setting up the Label Propagator object.
        :param graph: NetworkX object.
        :param args: Arguments object.
        """
        self.args = args
        self.seeding = args.seed
        self.rounds = args.rounds
        self.weight_setup(args.weighting)
        self.graph = graph
        self.nodes = [node for node in graph.nodes()]
        self.labels = {node: node for node in self.nodes}
        self.label_count = len(set(self.labels.values()))
        self.flag = True

    def weight_setup(self, weighting):
        """
        Calculating the edge weights.
        :param weighting: Type of edge weights.
        """
        if weighting == "overlap":
            self.weights = overlap_generator(overlap, self.graph)
        elif weighting == "unit":
            self.weights = overlap_generator(unit, self.graph)
        elif weighting == "min_norm":
            self.weights = overlap_generator(min_norm, self.graph)
        else:
            self.weights = overlap_generator(normalized_overlap, self.graph)

    def pick_neighbor(self, source, neighbors):
        """
        Choosing a neighbor from a propagation source node.
        :param source: Source node.
        :param neighbors: Neighboring nodes.
        """
        scores = {}
        for neighbor in neighbors:
            neighbor_label = self.labels[neighbor]
            scores[neighbor_label] = scores.setdefault(neighbor_label, 0.0) + self.weights[(neighbor, source)]
            # if neighbor_label in scores.keys():
            #     scores[neighbor_label] = scores[neighbor_label] + self.weights[(neighbor, source)]
            # else:
            #     scores[neighbor_label] = self.weights[(neighbor, source)]
        scores_items = list(scores.items())
        scores_items.sort(key=lambda x: x[1], reverse=True)

        # if there is not only one label with maximum count then choose one randomly
        labels = [(k, v) for k, v in scores_items if v == scores_items[0][1]]
        label = random.sample(labels, 1)[0][0]
        return label

    def do_a_propagation(self):
        """
        Doing a propagation round.
        """
        random.seed(self.seeding)
        random.shuffle(self.nodes)
        for node in tqdm(self.nodes):
            neighbors = self.graph.neighbors(node)
            self.labels[node] = self.pick_neighbor(node, neighbors)
        current_label_count = len(set(self.labels.values()))
        if self.label_count == current_label_count:
            self.flag = False
        else:
            self.label_count = current_label_count

    def start_label_propagation(self):
        """
        Doing propagations until convergence or reaching time budget.
        """
        index = 0
        while index < self.rounds and self.flag:
            index = index + 1
            print("\nLabel propagation round: " + str(index) + ".\n")
            self.do_a_propagation()
        print("end, next draw")
        # draw plot through networkx
        node_color = [float(self.labels[node]) for node in self.nodes]
        nx.draw_networkx(self.graph, node_color=node_color, node_size=150, alpha=1)
        plt.show()
        # print("Modularity is: " + str(round(modularity(self.labels, self.graph), 3)) + ".\n")
        json_dumper(self.labels, self.args.assignment_output)
