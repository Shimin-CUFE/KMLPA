"""Parsing the parameters."""

import argparse
import os

project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def parameter_parser():
    """
    A method to parse up command line parameters.
    By default it does community detection on the Facebook politicians network.
    """
    parser = argparse.ArgumentParser(description="Run Label Propagation.")

    parser.add_argument("--input",
                        nargs="?",
                        default=project_path + "\\data\\facebook.csv",
                        help="Input graph path.")

    parser.add_argument("--weighting",
                        nargs="?",
                        default="unit",
                        help="Unit weighting.")

    parser.add_argument("--rounds",
                        type=int,
                        default=20,
                        help="Number of iterations. Default is 20.")

    parser.add_argument("--seed",
                        type=int,
                        default=10,
                        help="Random seed. Default is 10.")

    return parser.parse_args()


def path():
    return project_path
