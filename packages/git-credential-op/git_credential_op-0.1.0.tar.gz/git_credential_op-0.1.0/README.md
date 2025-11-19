# git-credential-op

[![Changelog](https://img.shields.io/pypi/v/git-credential-op)](https://git.sr.ht/~nwgh/git-credential-op/log)
[![Tests](https://builds.sr.ht/~nwgh/git-credential-op.svg)](https://builds.sr.ht/~nwgh/git-credential-op?)
[![License](https://img.shields.io/badge/license-CC0%201.0-blue.svg)](https://git.sr.ht/~nwgh/git-credential-op/tree/main/item/LICENSE)

A simple `git credential` helper for 1password CLI (op)

## Installation

Install this tool using uv:

```bash
uv tool install git-credential-op
```

## Usage

For help, run:

```bash
git-credential-op --help
```

## Development

To contribute to this tool, first install `uv`. See [the uv documentation](https://docs.astral.sh/uv/getting-started/installation/) for how.

Next, checkout the code

```bash
git clone https://git.sr.ht/nwgh/git-credential-op
```

Then create a new virtual environment and sync the dependencies:

```bash
cd git-credential-op
uv sync
```

To run the tests:

```bash
uv run python -m pytest
```
