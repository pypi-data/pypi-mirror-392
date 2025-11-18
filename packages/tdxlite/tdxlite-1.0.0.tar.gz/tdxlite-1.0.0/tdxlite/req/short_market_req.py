from bitstring import BitArray

from .base_req import BaseReq
from ..constants import MsgType
from ..constants import Board


class ShortMarketReq(BaseReq):
    """快捷行情请求"""
    msg_type = MsgType.short_market

    def __init__(self, board: Board, start: int = 0, count: int = 0x50):
        super().__init__()
        self.board = board
        self.start = start
        self.count = count

    @property
    def msg_body(self) -> bytes:
        packet = BitArray()
        # <HHHHHHHHH> 映射
        packet.append(f"uintle:16={self.board}")
        packet.append(f"uintle:16=0")
        packet.append(f"uintle:16={self.start}")
        packet.append(f"uintle:16={self.count}")
        packet.append(f"uintle:16=0")
        packet.append(f"uintle:16=5")
        packet.append(f"uintle:16=0")
        packet.append(f"uintle:16=1")
        packet.append(f"uintle:16=0")
        return packet.bytes
