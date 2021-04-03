"""Run label propagation."""

from model import LabelPropagator
from param_parser import parameter_parser
from data_tools import graph_reader, argument_printer


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
    args = parameter_parser()
    argument_printer(args)
    create_and_run_model(args)
