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

This packages relies on YAML for configuration due to its readability, however it only parses a subset of it.
Here is what it looks like.

[`config.yaml`](./config.yaml)

```yaml
# An example configuration

string: "string"
int: 0
float: 0.0

# docstring
docstring: "value"

bool: true

empty: # int

nested:
  one: 1
  two: 2
```

- the top comments are the subcommand's description
- comments before a value are its docstring
- only `true` and `false` are valid booleans
- type hints can be specified for null values with an inline comment
- no lists
- nested values are flattened into a flat python dict, with keys joined by `_`

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

You can also use `cliyaml.call()` to call a function by giving it `kwargs` directly, it will only pass the correct arguments.
This function also allows you to pass named and list arguments to override the `kwargs`.

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

- [ ] Specify multiple config files in `@subcommand` to override / expand existing ones
