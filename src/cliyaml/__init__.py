"""Prototype projects fast with YAML configuration"""

# TODO :
# - override a config file with another config file ? (see how to merge trees ?) -> maybe not needed
# - call functions with only the needed arguments (helper to go faster)
# - register functions with decorators to be called as subcommands
# - auto register subcommands (importlib, could be cool)

from cliyaml.cli import build
from cliyaml.parse import parse_description, parse_lines


def configure(file: str):
    with open(file, "r") as f:
        content = f.read()
    lines = content.splitlines()
    data, _ = parse_lines(lines)

    return build(data, parse_description(lines))


# TODO : easily configure subcommands in subfiles ?
# like, auto import files in the script folder, and they define functions with a decorator that runs
# and registers the subcommand

if __name__ == "__main__":
    parser = configure("config.yaml")

    args = parser.parse_args()
    print(args)
