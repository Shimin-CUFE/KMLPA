"""Model class label propagation."""

import random
import time

from tqdm import tqdm

from data_tools import json_dumper, plot_printer
from weight_calculator import *
from modularity_calculator import modularity


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
        # read args and graph
        self.args = args
        self.graph = graph
        # pre-processing (old)
        self.nodes = [node for node in graph.nodes()]
        self.labels = {node: node for node in self.nodes}
        self.seeding = args.seed  # clear
        self.rounds = args.rounds
        self.weights = overlap_generator(normalized_overlap, self.graph)
        self.weight_setup(args.weighting)
        print("Drawing layout: spring_layout")
        self.layout = nx.spring_layout(self.graph)
        print("initialize done")

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
            pass

    def pre_processing(self):
        pass

    def post_processing(self):
        pass

    def do_single_propagation(self):
        """
        Doing a propagation round.
        """
        # random.seed(self.seeding)
        # random.shuffle(self.nodes)
        for node in tqdm(self.nodes):
            neighbors = self.graph.neighbors(node)
            self.labels[node] = self.pick_neighbor(node, neighbors)

    def pick_neighbor(self, source, neighbors):
        """
        Choosing a neighbor from a propagation source node.
        :param source: Source node.
        :param neighbors: Neighboring nodes.
        """
        # Need to ReFactor
        scores = {}
        for neighbor in neighbors:
            neighbor_label = self.labels[neighbor]
            scores[neighbor_label] = scores.setdefault(neighbor_label, 0.0) + self.weights[(neighbor, source)]
        scores_items = list(scores.items())
        scores_items.sort(key=lambda x: x[1], reverse=True)

        # if there is not only one label with maximum count then choose one randomly
        labels = [(k, v) for k, v in scores_items if v == scores_items[0][1]]
        label = random.sample(labels, 1)[0][0]
        return label

    def estimate_stop_cond(self):
        for node in self.nodes:
            count = {}
            for neighbor in self.graph.neighbors(node):
                neighbor_label = self.labels[neighbor]
                count[neighbor_label] = count.setdefault(neighbor_label, 0.0) + self.weights[(neighbor, node)]
            # find out labels with maximum count
            count_items = list(count.items())
            count_items.sort(key=lambda x: x[1], reverse=True)
            # if there is not only one label with maximum count then choose one randomly
            labels = [k for k, v in count_items if v == count_items[0][1]]
            if self.labels[node] not in labels:
                return False
        return True

    def start_label_propagation(self):
        """
        Doing propagations until convergence or reaching time budget.
        """
        lpastart = time.clock()

        self.pre_processing()  # Pre processing before propagation:
        index = 0
        while True:
            # input("Press enter to continue...")
            index += 1
            print("\nLabel propagation round: " + str(index) + ".\n")
            self.do_single_propagation()
            print("Stop condition :" + str(self.estimate_stop_cond()))

            # # Draw plot every round
            # image_printer(self.layout, self.graph, self.nodes, self.labels)

            if index > self.rounds or self.estimate_stop_cond() is True:
                break
        self.post_processing()  # Post processing after propagation:

        lpaend = time.clock()

        label_count = len(set(self.labels.values()))
        print("end, count is %s, CPU time is %f" % (label_count, (lpaend - lpastart)))
        # print(set(self.labels.values()))

        # Draw plot
        plot_printer(self.graph, self.layout, self.nodes, self.labels)

        # Calculate modularity
        print("Modularity is: " + str(modularity(self.graph, self.labels)))

        json_dumper(self.labels, self.args.assignment_output)
