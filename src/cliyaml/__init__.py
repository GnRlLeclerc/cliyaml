"""Prototype projects fast with YAML configuration, and some additional utilities."""

import inspect
from argparse import ArgumentParser
from typing import Any, Callable, TypeVar

from cliyaml.cli import add_to_parser
from cliyaml.parse import Tree, parse_lines, to_dict
from cliyaml.source import source

# Registered commands
__commands__ = {}

# Main command parser
__parser__: ArgumentParser | None = None
__subparser__: Any = None


def initialize(parser: ArgumentParser | None = None, *paths: str):
    """Initialize the main argument parser"""
    global __parser__, __subparser__

    if parser is None:
        __parser__ = ArgumentParser()
    else:
        __parser__ = parser

    __subparser__ = __parser__.add_subparsers(help="Subcommands", dest="subcommand")

    # Import all python files under the specified paths to register subcommands automatically
    source(*paths)


def _merge_trees(base: Tree, new: Tree) -> Tree:
    """Recursively merge two YAML trees in a type-safe way"""

    for key, new_node in new.items():
        if key in base:
            base_node = base[key]
            if base_node.type == dict and new_node.type == dict:
                assert isinstance(base_node.value, dict)
                assert isinstance(new_node.value, dict)
                _merge_trees(base_node.value, new_node.value)
            elif base_node.type == new_node.type:
                base[key] = new_node
            else:
                raise TypeError(
                    f"Type mismatch for key '{key}': {base_node.type} vs {new_node.type}"
                )
        else:
            base[key] = new_node
    return base


def subcommand(*files: str):
    """Register a function as a subcommand, with config taken from the specified file"""

    tree: Tree = {}

    for file in files:
        with open(file, "r") as f:
            lines = f.readlines()

        new_tree, _ = parse_lines(lines)

        if not tree:
            tree = new_tree
        else:
            tree = _merge_trees(tree, new_tree)

    def decorator(func):
        description = func.__doc__
        if __parser__ is None:
            raise ValueError(
                "Call `cliyaml.initialize` before registering subcommands with the `subcommand` decorator"
            )

        name = func.__name__.replace("_", "-")

        __commands__[name] = func
        parser = __subparser__.add_parser(name, help=description)
        add_to_parser(parser, tree)
        parser.add_argument(
            "-c",
            "--config",
            type=str,
            help="Path to a YAML config file to override default values",
        )

    return decorator


def handle():
    """Handle cli arguments and run the correct subcommand"""

    if __parser__ is None:
        raise ValueError(
            "Call `cliyaml.initialize` before parsing cli arguments with `cliyaml.handle`"
        )

    args = __parser__.parse_args()
    subcommand = args.subcommand

    if subcommand is None:
        return

    if args.config is not None:
        with open(args.config, "r") as f:
            content = f.read()
        lines = content.splitlines()
        data, _ = parse_lines(lines)

        additional = to_dict(data)
    else:
        additional = {}

    del args.config  # type: ignore
    del args.subcommand  # type: ignore

    # Override args only if types are compatible
    kwargs = vars(args)
    for key, value in additional.items():
        if key not in kwargs:
            raise KeyError(f"Extra option passed '{key}' in override config file")
        base = kwargs[key]
        if type(value) == type(base) or base is None or value is None:
            kwargs[key] = value
        else:
            raise TypeError(
                f"Type mismatch for option '{key}': expected {type(base)}, got {type(value)}"
            )

    __commands__[subcommand](**kwargs)


R = TypeVar("R")


def call(func: Callable[..., R], d: dict, *args, **kwargs) -> R:
    """Call a function with the exact arguments it needs from a dict.
    Arguments can be manually specified as well."""
    merged = d | kwargs
    sig = inspect.signature(func)
    filtered_kwargs = {k: v for k, v in merged.items() if k in sig.parameters}

    return func(*args, **filtered_kwargs)
