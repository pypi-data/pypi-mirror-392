# tdxlite

[![PyPI - Version](https://img.shields.io/pypi/v/tdxlite.svg)](https://pypi.org/project/tdxlite)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tdxlite.svg)](https://pypi.org/project/tdxlite)

-----

## Table of Contents

- [Installation](#installation)
- [Introduction](#start)
- [License](#license)

## Installation

```console
pip install tdxlite
```

## Introduction

### 示例1：获取北交所成分股

```python
from tdxlite.client import TdxClient

with TdxClient() as client:
    stock_list = client.get_stock_list_bj()
    print(stock_list)
    print(len(stock_list))
```

## License

`tdxlite` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
