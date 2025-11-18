from enum import IntEnum


class Board(IntEnum):
    """市场板块"""
    SH = 0      # 上证
    SZ = 2      # 深证
    BJ = 12     # 北证
    A = 6       # A股
    KCB = 8     # 科创板
    CYB = 14    # 创业板
