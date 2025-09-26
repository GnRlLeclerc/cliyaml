import importlib.util
from pathlib import Path


def source(*paths: str):
    """Recursively run python files in directories or subdirectories,
    without regitering them as modules."""

    for path in paths:
        p = Path(path)
        if p.is_file():
            run_file(str(p))
        else:
            for file in p.rglob("*.py"):
                run_file(str(file))


def run_file(path: str):
    p = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(p.stem, str(p))
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
