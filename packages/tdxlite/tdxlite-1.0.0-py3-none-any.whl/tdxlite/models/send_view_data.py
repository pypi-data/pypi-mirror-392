from dataclasses import dataclass


@dataclass
class SendViewData:
    """请求视图数据对象"""

    msg_prefix: str
    msg_seq: str
    msg_type: str
    msg_body: str
