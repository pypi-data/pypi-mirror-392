from enum import StrEnum


class RadarEngineMode(StrEnum):
    """雷达引擎模式"""
    REALTIME = "realtime"  # 实时模式
    REPLAY = "replay"  # 回放模式
