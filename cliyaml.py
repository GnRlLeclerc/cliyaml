""" """

from cli import build
from parse import parse_description, parse_lines


def configure(file: str):
    with open(file, "r") as f:
        content = f.read()
    lines = content.splitlines()
    data, _ = parse_lines(lines)

    return build(data, parse_description(lines))


if __name__ == "__main__":
    parser = configure("config.yaml")

    args = parser.parse_args()
    print(args)
