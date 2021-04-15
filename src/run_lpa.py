"""Run label propagation."""

import sys
import time

from data_tools import graph_reader, argument_printer
from model import LabelPropagator
from param_parser import parameter_parser, path


class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


def create_and_run_model(args):
    """
    创建图、LPA模型实例，运行LPA模型
    Method to run the model.
    :param args: Arguments object.
    """
    graph = graph_reader(args.input)
    model = LabelPropagator(graph, args)
    model.label_propagation()


if __name__ == "__main__":
    t = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    sys.stdout = Logger(path() + "\\output\\log\\" + t + "_log.log", sys.stdout)
    # sys.stderr = Logger(path() + "\\output\\log\\" + t + "_error.log", sys.stderr)
    args = parameter_parser()
    argument_printer(args)
    create_and_run_model(args)
