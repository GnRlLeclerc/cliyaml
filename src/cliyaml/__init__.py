"""Prototype projects fast with YAML configuration, and some additional utilities."""

import inspect
from argparse import ArgumentParser
from typing import Any, Callable, ParamSpec, TypeVar

from cliyaml.cli import add_to_parser, build
from cliyaml.parse import parse_description, parse_lines, to_dict
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


def configure(file: str):
    with open(file, "r") as f:
        content = f.read()
    lines = content.splitlines()
    data, _ = parse_lines(lines)

    return build(data, parse_description(lines))


def subcommand(file: str):
    """Register a function as a subcommand, with config taken from the specified file"""

    with open(file, "r") as f:
        lines = f.readlines()

    def decorator(func):
        if __parser__ is None:
            raise ValueError(
                "Call `cliyaml.initialize` before registering subcommands with the `subcommand` decorator"
            )

        __commands__[func.__name__] = func
        parser = __subparser__.add_parser(func.__name__, help=parse_description(lines))
        tree, _ = parse_lines(lines)
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

    kwargs = vars(args) | additional

    __commands__[subcommand](**kwargs)


def override(base: dict, new: dict) -> dict:
    """Deeply override values from a base dict with values from another dict.
    Done in place for the base dict."""

    for key, value in new.items():
        if "key" in base and isinstance(base[key], dict) and isinstance(new[key], dict):
            override(base[key], new[key])
        else:
            base[key] = value

    return base


P = ParamSpec("P")
R = TypeVar("R")


def call(func: Callable[P, R], d: dict, *args: P.args, **kwargs: P.kwargs) -> R:
    """Call a function with the exact arguments it needs from a dict.
    Arguments can be manually specified as well."""
    merged = d | kwargs
    sig = inspect.signature(func)
    filtered_kwargs = {k: v for k, v in merged.items() if k in sig.parameters}

    return func(*args, **filtered_kwargs)
