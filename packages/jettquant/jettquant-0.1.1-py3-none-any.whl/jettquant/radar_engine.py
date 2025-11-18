import time
from typing import Callable, Generator
import threading
import pyarrow.parquet as pq
import json

import pandas as pd
from xtquant import xtdata

from .event import Event, EventEngine, EVENT_TIMER
from .event.event_type import EVENT_ALL_TICK
from .constants import RadarEngineMode


class RadarEngine:
    """雷达引擎: 实时行情推送服务"""

    def __init__(
            self,
            event_engine: EventEngine | None = None,
            is_verbose: bool = False,
            output: Callable = print
    ):

        if event_engine is None:
            event_engine = EventEngine(interval=3)
        self.event_engine = event_engine

        if is_verbose:
            pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
            pd.set_option('display.max_rows', 1000)  # 最多显示数据的行数

        self.is_verbose = is_verbose
        self.output = output

        # 订阅标的列表
        self.subscribed_xt_symbols: set[str] = set()
        self._lock = threading.Lock()

        # 运行模式
        self.mode: RadarEngineMode = RadarEngineMode.REALTIME

        # 回放功能
        self.replay_generator: Generator | None = None
        self.replay_file_path: str | None = None
        self.replay_data_batch_size: int = 100

        self.event_engine.register(EVENT_TIMER, self.on_timer)

    def set_mode(self, mode: RadarEngineMode):
        """设置引擎模式"""
        with self._lock:
            old_mode = self.mode
            self.mode = mode
            self.output(f"雷达引擎模式切换: {old_mode.value} -> {mode.value}")

    def set_data_path(self, file_path: str):
        self.replay_file_path = file_path

    def subscribe_all(self, callback: Callable):
        """订阅全市场"""

        def on_all_tick(event: "Event"):
            callback(event.edata)

        # 注册市场数据处理器
        self.event_engine.register(EVENT_ALL_TICK, on_all_tick)

    def subscribe(self, xt_symbols: str | list[str], callback: Callable):
        """订阅标的"""

        def func(event: Event):
            callback(event.edata)

        if isinstance(xt_symbols, str):
            xt_symbols = [xt_symbols]

        with self._lock:
            for xt_symbol in xt_symbols:
                if xt_symbol not in self.subscribed_xt_symbols:
                    self.subscribed_xt_symbols.add(xt_symbol)

                    event_type = f"{EVENT_ALL_TICK}{xt_symbol}"
                    self.event_engine.register(event_type, func)

                    self.output(fr"订阅标的：{xt_symbol}")

    def unsubscribe(self, xt_symbols: str | list[str]):
        """取消订阅"""
        if isinstance(xt_symbols, str):
            xt_symbols = [xt_symbols]

        with self._lock:
            for xt_symbol in xt_symbols:
                if xt_symbol in self.subscribed_xt_symbols:
                    self.subscribed_xt_symbols.discard(xt_symbol)
                    self.output(fr"取消订阅标的：{xt_symbol}")

    def get_subscribed(self) -> list[str]:
        """获取当前订阅列表"""
        with self._lock:
            return sorted(self.subscribed_xt_symbols)

    def subscribe_sector(self, sector_name: str):
        """订阅板块所有成分股: """
        raise NotImplementedError

    def fetch_realtime_segment(self) -> dict:
        """实时数据切片"""
        stock_list = xtdata.get_stock_list_in_sector("沪深A股")
        data_dict: dict = xtdata.get_full_tick(stock_list)
        return data_dict

    def fetch_history_segment(self) -> dict | None:
        """回访数据切片"""
        if not self.replay_generator:
            return None

        try:
            # 从生成器获取下一条数据
            ts, tick_dict = next(self.replay_generator)
            return tick_dict
        except StopIteration:
            return None  # 回放结束
        except Exception as e:
            self.output(f"回放数据读取异常: {e}")
            return None

    def create_replay_generator(self, file_path: str):
        parquet_file = pq.ParquetFile(file_path)

        for batch in parquet_file.iter_batches(batch_size=self.replay_data_batch_size):
            ts_arr = batch.column("ts")
            json_arr = batch.column("json")

            # 直接对 column 的 Python 标量进行处理，避免复制 Arrow table
            for i in range(batch.num_rows):
                yield ts_arr[i].as_py(), json.loads(json_arr[i].as_py())

            # 显式释放 batch（重要！）
            del batch

    def start_replay(self, file_path: str):
        """数据回访"""

        if self.mode == RadarEngineMode.REPLAY:
            self.output("已在回放模式,请先停止")
            return False

        try:
            # 检查文件
            from pathlib import Path
            if not Path(file_path).exists():
                self.output(f"回放文件不存在: {file_path}")
                return False

            # 初始化回放状态
            self.replay_file_path = file_path
            self.replay_generator = self.create_replay_generator(file_path)

            # 切换为回访模式
            self.set_mode(RadarEngineMode.REPLAY)

            self.output(f"开始回放: {file_path}")
            return True

        except Exception as e:
            self.output(f"启动回放失败: {e}")
            self.reset_replay_state()
            return False

    def stop_replay(self):
        """停止回放"""
        if self.mode != RadarEngineMode.REPLAY:
            return

        self.reset_replay_state()

        self.set_mode(RadarEngineMode.REALTIME)

    def reset_replay_state(self):
        """重置回访状态"""
        self.replay_generator = None
        self.replay_file_path = None

    def on_timer(self, event: Event):
        """定时触发逻辑"""
        try:
            if self.mode == RadarEngineMode.REALTIME:
                data_dict = self.fetch_realtime_segment()

                if not data_dict:
                    self.output(fr"行情数据为空")
                    return
            else:
                data_dict = self.fetch_history_segment()

                if data_dict is None:
                    self.output("回放数据已全部推送完毕")
                    self.stop_replay()
                    return

            # 推送事件: 全市场数据
            event = Event(EVENT_ALL_TICK, data_dict)
            self.event_engine.put(event)

            # 推送事件: 订阅标的数据
            self.handle_singe_tick(data_dict)

        except Exception as e:
            self.output(fr"获取全推行情数据失败：{e}")
            if self.mode == RadarEngineMode.REPLAY:
                self.stop_replay()

    def handle_singe_tick(self, data_dict: dict):
        with self._lock:
            subs = list(self.subscribed_xt_symbols)

        for xt_symbol in subs:
            if xt_symbol in data_dict:
                tick_data = data_dict[xt_symbol]

                # 构造事件类型
                event_type = f"{EVENT_ALL_TICK}{xt_symbol}"
                event = Event(event_type, tick_data)
                self.event_engine.put(event)

    def run_forever(self):
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            self.output(f"行情引擎被手动中断")
        except Exception as e:
            self.output(f"行情引擎运行异常：{e}")
        finally:
            self.event_engine.stop()

    def start(self):
        # 启动事件引擎
        self.event_engine.start()
