# jettquant

[![PyPI - Version](https://img.shields.io/pypi/v/jettquant.svg)](https://pypi.org/project/jettquant)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jettquant.svg)](https://pypi.org/project/jettquant)

-----

## Table of Contents

- [Installation](#installation)
- [Introduction](#project-structure)
- [License](#license)

## Installation

```console
pip install jettquant
```

## Introduction

### 示例1：订阅全市场数据
```python
from jettquant import RadarEngine

market_engine = RadarEngine(is_verbose=True)


def on_all_tick(data: dict):
    """每3秒推送一次截面数据"""
    print(data)
    

market_engine.subscribe_all(on_all_tick)

market_engine.start()
market_engine.run_forever()
```

### 示例2：订阅单只标的
```python
from jettquant import RadarEngine

market_engine = RadarEngine()


def func(data_dict: dict):
    """订阅单只标的"""
    print(data_dict)


xt_symbol = ["300750.SZ"]
market_engine.subscribe(xt_symbol, func)

market_engine.start()
market_engine.run_forever()
```

### 示例3：数据回放
```python
from pandas import DataFrame

from jettquant import EventEngine, RadarEngine

event_engine = EventEngine(interval=0.3)  # 10倍回放数据
radar = RadarEngine(event_engine=event_engine, is_verbose=True)


def on_all_tick(data):
    df = (
        DataFrame.from_dict(data)
        .T.reset_index()
        .rename(columns={'index': '证券代码'})
    )

    radar.output(fr"接收到全推数据: {df.head(5)}")


radar.subscribe_all(on_all_tick)

# 开始回放
radar.start_replay("tick_parquet_daily/ticks-2025-11-14.parquet")

radar.start()
radar.run_forever()
```


## License

`jettquant` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
