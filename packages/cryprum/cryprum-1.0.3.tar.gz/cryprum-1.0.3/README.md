# Cryprum client, for Python 3

![PyPI](https://img.shields.io/pypi/v/cryprum)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cryprum)

## Installation

```
pip install cryprum
```

## Usage

Create a token https://cryprum.com/tokens and copy "Access key"

```python
from cryprum import Client

cl = Client(token="<ACCESS_KEY>")
```

```python
from cryprum import AsyncClient

cl = AsyncClient(token="<ACCESS_KEY>")
```

## Run tests

```
CRYPRUM_TOKEN=<token> pytest -v tests.py
```
