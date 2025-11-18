from enum import StrEnum


class MsgType(StrEnum):
    """协议消息类型"""
    beat_heart = "0d00"     # 心跳
    short_market = "4b05"   # 快捷行情
