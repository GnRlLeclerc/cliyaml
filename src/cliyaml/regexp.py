"""Regular expressions to parse YAML values"""

import re

int = re.compile(r"^-?([0-9_]+)")
float = re.compile(r"^-?([0-9_]*\.[0-9_]*)")
boolean = re.compile(r"^(true|false)")
string = re.compile(r'"([^"]*)"')


def match(s: str, re: re.Pattern[str]) -> str | None:
    """Match a regex at the start of a string, return the matched part or None"""

    m = re.match(s)

    if m is None:
        return None

    return m.group(0)
