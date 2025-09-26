# CliYaml

Prototype projects fast with YAML configuration, override it with CLI.

The idea of this package is to make building reusable, copiable, and configurable scripts in a very fast and readable way.

For instance, this is especially useful when iterating on `pytorch` model designs and training loops,
using separate scripts that can easily be modified, copied, while keeping a readable YAML & CLI api for running them with various configurations.

Basically:

1. Define a typed default config in a subset of YAML (put paths, devices, epochs, learning rates there...)
2. Define cli subcommands that each refer to a config file using the `@subcommand("file.yaml")` decorator
3. Register subcommands, parse cli args and run the correct subcommands using `initialize()` and `handle()`

## Usage

### YAML subset

TODO

### CLI API

Define some scripts in separate files, for instance in a `scripts/` folder.

`scripts/main.py`:

```python
from cliyaml import subcommand

@subcommand("config.yaml")
def main(**kwargs):
    print("Called with args:", kwargs)
```

In your `main.py`, include the following code:

```python
if __name__ == "__main__":
    import cliyaml

    # Registers subcommands
    # NOTE: you can also register single files
    cliyaml.initialize(None, "scripts/")

    # Parses CLI args and runs commands
    cliyaml.handle()
```

Then, run the following code to use your API:

```bash
python main.py -h
python main.py main -h
python main.py main
```

## Building

```bash
uv build
```

## Publish

TODO

## Test

```bash
pytest
```

## Roadmap

- [ ] Type & Key checking when overriding configs using `--config`
- [ ] Specify multiple config files in `@subcommand` to override / expand existing ones
