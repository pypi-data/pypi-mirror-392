from .base_req import BaseReq
from ..constants import MsgType


class BeatHeartReq(BaseReq):
    """心跳请求"""
    msg_type = MsgType.beat_heart

    @property
    def msg_body(self) -> bytes:
        return b'\x01'
