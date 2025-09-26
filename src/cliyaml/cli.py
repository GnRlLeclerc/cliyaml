"""Convert a config tree to argparse command-line arguments."""

import argparse

from cliyaml.parse import Tree


def build(tree: Tree, description: str = "") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    add_to_parser(parser, tree)

    return parser


def add_to_parser(
    parser: argparse.ArgumentParser, tree: Tree, prefix="", prefix_shorthand=""
):
    """Recursively traverse the tree and add arguments to the parser."""

    prefix_shorthands = set()
    shorthands = set()

    for key, value in tree.items():
        if isinstance(value.value, dict):
            shortand = get_shorthand(key, prefix_shorthands)
            add_to_parser(
                parser, value.value, f"{prefix}{key}-", f"{prefix_shorthand}{shortand}-"
            )
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

        shorthand = get_shorthand(key, shorthands)

        parser.add_argument(
            f"-{prefix_shorthand}{shorthand}", f"--{prefix}{key}", **args
        )


def get_shorthand(key: str, used: set[str]) -> str:
    """Get a unique shorthand for a key."""
    i = 1
    while (shorthand := key[0:i]) in used:
        i += 1
    used.add(shorthand)
    return shorthand
