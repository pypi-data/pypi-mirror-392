from pandas import DataFrame
import numpy as np

from jettquant import EventEngine, RadarEngine

event_engine = EventEngine(interval=0.03)  # 10倍回放数据
radar_engine = RadarEngine(event_engine=event_engine, is_verbose=True)


def calculate_auction_metrics_vectorized(df):
    """
    向量化计算集合竞价指标
    性能优化版本，适用于大批量数据
    """
    # 提取列表类型的数据
    ask_prices = df['askPrice'].values
    bid_prices = df['bidPrice'].values
    ask_vols = df['askVol'].values
    bid_vols = df['bidVol'].values
    last_closes = df['lastClose'].values

    # 初始化结果数组
    n = len(df)
    match_prices = np.zeros(n)
    auction_volumes = np.zeros(n, dtype=int)
    auction_amounts = np.zeros(n)
    price_change_pcts = np.zeros(n)
    unmatched_volumes = np.zeros(n, dtype=int)

    # 向量化提取第一档价格和量
    for i in range(n):
        # 匹配价格（买一或卖一）
        if isinstance(ask_prices[i], list) and len(ask_prices[i]) > 0 and ask_prices[i][0] > 0:
            match_prices[i] = ask_prices[i][0]
        elif isinstance(bid_prices[i], list) and len(bid_prices[i]) > 0 and bid_prices[i][0] > 0:
            match_prices[i] = bid_prices[i][0]

        # 第一档买卖量
        bid_vol_1 = bid_vols[i][0] if isinstance(bid_vols[i], list) and len(bid_vols[i]) > 0 else 0
        ask_vol_1 = ask_vols[i][0] if isinstance(ask_vols[i], list) and len(ask_vols[i]) > 0 else 0

        # 竞价量 = min(买一, 卖一)
        auction_volumes[i] = min(bid_vol_1, ask_vol_1)

        # 所有档位总量
        total_bid = sum([v for v in bid_vols[i] if isinstance(v, (int, float)) and v > 0]) if isinstance(bid_vols[i],
                                                                                                         list) else 0
        total_ask = sum([v for v in ask_vols[i] if isinstance(v, (int, float)) and v > 0]) if isinstance(ask_vols[i],
                                                                                                         list) else 0
        unmatched_volumes[i] = total_bid - total_ask

    # 向量化计算金额和涨幅
    auction_amounts = auction_volumes * match_prices * 100

    # 避免除零
    valid_close = last_closes > 0
    price_change_pcts[valid_close] = (match_prices[valid_close] - last_closes[valid_close]) / last_closes[
        valid_close] * 100

    # 构建结果DataFrame（只保留关键列）
    result = DataFrame({
        '证券代码': df['证券代码'].values,
        '时间': df['timetag'].values,
        '昨收': last_closes,
        '匹配价格': match_prices,
        '竞价量': auction_volumes,
        '竞价金额': auction_amounts,
        '竞价涨幅': price_change_pcts,
        '未匹配量': unmatched_volumes
    })

    return result


def on_all_tick(data):
    df = (
        DataFrame.from_dict(data)
        .T.reset_index()
        .rename(columns={'index': '证券代码'})
    )

    # 计算集合竞价指标
    df_auction = calculate_auction_metrics_vectorized(df)

    # 只输出有竞价的股票（竞价量>0）
    active_df = df_auction[df_auction['竞价量'] > 0].copy()

    if not active_df.empty:
        # 按竞价金额排序
        active_df = active_df.sort_values('竞价金额', ascending=False)

        # 格式化输出
        active_df['竞价金额'] = active_df['竞价金额'].apply(lambda x: f"{x:,.0f}")
        active_df['竞价涨幅'] = active_df['竞价涨幅'].apply(lambda x: f"{x:.2f}%")

        radar_engine.output(active_df)
    else:
        radar_engine.output("无活跃竞价数据")


radar_engine.subscribe_all(on_all_tick)

# 开始回放
radar_engine.start_replay("ticks-2025-11-14-auction.parquet")

radar_engine.start()
radar_engine.run_forever()
