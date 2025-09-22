"""Prototype projects fast with YAML configuration"""

# TODO :
# - call functions with only the needed arguments (helper to go faster)
# - register functions with decorators to be called as subcommands
# - auto register subcommands (importlib, could be cool)

from argparse import ArgumentParser
from typing import Any

from cliyaml.cli import add_to_parser, build
from cliyaml.parse import parse_description, parse_lines

# Registered commands
__commands__ = {}

# Main command parser
__parser__: ArgumentParser | None = None
__subparser__: Any = None


def initialize(parser: ArgumentParser | None = None):
    """Initialize the main argument parser"""
    global __parser__, __subparser__

    if parser is None:
        __parser__ = ArgumentParser()
    else:
        __parser__ = parser

    __subparser__ = __parser__.add_subparsers(help="Subcommands", dest="subcommand")


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

    del args.subcommand  # type: ignore
    __commands__[subcommand](**vars(args))


def override(base: dict, new: dict) -> dict:
    """Deeply override values from a base dict with values from another dict.
    Done in place for the base dict."""

    for key, value in new.items():
        if "key" in base and isinstance(base[key], dict) and isinstance(new[key], dict):
            override(base[key], new[key])
        else:
            base[key] = value

    return base


if __name__ == "__main__":
    initialize()

    @subcommand("config.yaml")
    def f(**_):
        print("ok")

    handle()
