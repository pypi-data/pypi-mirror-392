from jettquant import RadarEngine

market_engine = RadarEngine(is_verbose=True)


def on_all_tick(data: dict):
    """每3秒推送一次截面数据"""
    print(data)


# 订阅全推数据
market_engine.subscribe_all(on_all_tick)


def on_tick(data: dict):
    """每3秒推送一次截面数据"""
    print(data)


# 订阅单只标的
market_engine.subscribe("300750.SZ", on_tick)

market_engine.start()
market_engine.run_forever()
