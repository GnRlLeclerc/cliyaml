"""Convert a config tree to argparse command-line arguments."""

import argparse

from parse import Tree


def build(tree: Tree, description: str = "") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    add_to_parser(parser, tree)

    return parser


def add_to_parser(parser: argparse.ArgumentParser, tree: Tree, prefix=""):
    """Recursively traverse the tree and add arguments to the parser."""

    for key, value in tree.items():
        if isinstance(value.value, dict):
            add_to_parser(parser, value.value, f"{prefix}{key}-")
            continue

        args: dict = {
            "help": value.comment,
        }
        if value.type == bool:
            args["action"] = "store_true"
        else:
            args["type"] = value.type

        if value.value is not None:
            args["default"] = value.value

        parser.add_argument(f"--{prefix}{key}", **args)
