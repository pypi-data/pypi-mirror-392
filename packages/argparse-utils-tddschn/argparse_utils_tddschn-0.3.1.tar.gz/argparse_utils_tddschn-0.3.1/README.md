# Argparse Utils (tddschn)

Utilities for dynamically removing or renaming argparse arguments without rewriting the original CLI definition.

## Features
- Remove an option (including from mutually exclusive groups) by dest or option string.
- Replace an argument's option strings atomically with conflict detection.

## Installation
```bash
pip install argparse-utils-tddschn
```

## Usage
```python
import argparse
from argparse_utils import remove_argument, replace_argument_names

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config")
parser.add_argument("--dry-run", action="store_true")

remove_argument(parser, "--dry-run")
replace_argument_names(parser, "--config", ["-C", "--configuration"])
```

### Presetting Arguments

Sometimes you want to provide default argument values programmatically, for example when centralizing configuration or writing tests. The `preset_arguments` helper lets you do this by pretending the supplied tokens were passed on the command line.

Important points:
- Provide a sequence of tokens (not a single string) such as `['--config', 'foo.ini', '--dry-run']`.
- Flags and value-style options are supported; positional arguments are supported too.
- Unknown tokens will raise a `ValueError`.
- If you pass a raw string instead of a token sequence, a `TypeError` is raised.
- Presets are applied as parser defaults using `parser.set_defaults(...)`, so actual CLI values still override them.

Example:

```python
from argparse import ArgumentParser
from argparse_utils import preset_arguments

parser = ArgumentParser(prog="prog")
parser.add_argument("-c", "--config")
parser.add_argument("--dry-run", action="store_true")

# Pretend the user passed these on the command line
preset_arguments(parser, ["--config", "foo.ini", "--dry-run"])

args = parser.parse_args([])
assert args.config == "foo.ini"
assert args.dry_run is True

# CLI still wins over preset
args = parser.parse_args(["--config", "bar.ini"])
assert args.config == "bar.ini"
assert args.dry_run is True
```

## Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## License
MIT