import os
import sys
import random
import networkx as nx
import matplotlib.pyplot as plt


def read_graph_from_file(path):
    # read edge-list from file
    graph = nx.read_edgelist(path, data=(('weight', float),))
    # initial graph node's attribute 'label' with its id
    for node, data in graph.nodes(True):
        data['label'] = node
    return graph


def read_game_info_from_file(path):
    game = {}

    with open(path, 'r', encoding='UTF-8') as f:
        for line in f:
            line = line.strip()
            data = line.split('\t')
            game[data[0]] = data[1]

    return game


# label-propagation algorithm
# use asynchronous updating for better results
def lpa(graph):
    def estimate_stop_cond():
        for node in graph.nodes():
            count = {}
            for neighbor in graph.neighbors(node):
                neighbor_label = graph.nodes[neighbor]['label']
                neighbor_weight = graph.edges[node, neighbor]['weight']
                count[neighbor_label] = count.setdefault(neighbor_label, 0.0) + neighbor_weight

            # find out labels with maximum count
            count_items = list(count.items())
            count_items.sort(key=lambda x: x[1], reverse=True)

            # if there is not only one label with maximum count then choose one randomly
            labels = [k for k, v in count_items if v == count_items[0][1]]

            if graph.nodes[node]['label'] not in labels:
                return False

        return True

    loop_count = 0

    while True:
        loop_count += 1
        print('loop', loop_count)

        for node in graph.nodes():
            count = {}

            for neighbor in graph.neighbors(node):
                neighbor_label = graph.nodes[neighbor]['label']
                neighbor_weight = graph.edges[node, neighbor]['weight']
                count[neighbor_label] = count.setdefault(neighbor_label, 0.0) + neighbor_weight

            # find out labels with maximum count
            count_items = list(count.items())
            count_items.sort(key=lambda x: x[1], reverse=True)

            # if there is not only one label with maximum count then choose one randomly
            labels = [(k, v) for k, v in count_items if v == count_items[0][1]]
            label = random.sample(labels, 1)[0][0]

            graph.nodes[node]['label'] = label

        if estimate_stop_cond() is True or loop_count >= 10:
            print('complete')
            return


def print_graph_info(graph):
    game_info = read_game_info_from_file(project_path + '\\data\\id_name.info')
    info = {}

    for node, data in graph.nodes(True):
        info.setdefault(graph.nodes[node]['label'], []).append(game_info.get(node, node))

    print('node num:', len(graph.nodes(True)))
    print('class num:', len(info.keys()))
    print('class:', info.keys())
    print('info:')
    for clazz in info:
        print('\t%s(%d):' % (clazz, len(info[clazz])), )
        for label in info[clazz]:
            print('\'%s\'' % label, )
        print('\n', )


if __name__ == '__main__':
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0]))))
    g = read_graph_from_file(project_path + '\\data\\d.data')
    lpa(g)
    print_graph_info(g)

    node_color = [float(g.nodes[v]['label']) for v in g]
    labels = dict([(node, node) for node, data in g.nodes(True)])
    nx.draw_networkx(g, node_color=node_color)
    plt.show()
