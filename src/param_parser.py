"""Parsing the parameters."""

import argparse
import os
import sys

project_path = os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0])))


def parameter_parser():
    """
    A method to parse up command line parameters. By default it does community detection on the Facebook politicians network.
    The default hyperparameters give a good quality clustering. Default weighting happens by neighborhood overlap.
    """
    parser = argparse.ArgumentParser(description="Run Label Propagation.")

    parser.add_argument("--input",
                        nargs="?",
                        default=project_path + "\\data\\d.csv",
                        help="Input graph path.")

    parser.add_argument("--assignment-output",
                        nargs="?",
                        default=project_path + "\\output\\d.json",
                        help="Assignment path.")

    parser.add_argument("--weighting",
                        nargs="?",
                        default="unit",
                        help="Unit weighting.")

    parser.add_argument("--rounds",
                        type=int,
                        default=10,
                        help="Number of iterations. Default is 10.")

    parser.add_argument("--seed",
                        type=int,
                        default=42,
                        help="Random seed. Default is 42.")

    return parser.parse_args()
