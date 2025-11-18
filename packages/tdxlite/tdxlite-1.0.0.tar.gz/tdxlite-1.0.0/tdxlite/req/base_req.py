from abc import abstractmethod

from bitstring import ConstBitStream, BitArray

from ..utils import get_msg_seq
from ..constants import ProtocolSpec
from ..models import SendViewData


class BaseReq:
    """请求协议基类: 负责请求协议打包，子类需要实现msg_body方法"""
    msg_type: str  # 消息类型

    def __init__(self, msg_seq: str | None = None) -> None:
        self.msg_seq = msg_seq or get_msg_seq()

    @property
    def body_len(self) -> int:
        """计算消息体长度: msg_id(2字节) + msg_body长度"""
        return 2 + len(self.msg_body)

    @property
    @abstractmethod
    def msg_body(self) -> bytes:
        """业务子类来覆写"""
        raise NotImplementedError()

    def to_bytes(self, unknown: int = 0x01) -> bytes:
        """统一生成二进制协议数据包"""
        body_len = self.body_len

        # 构建数据包
        packet = BitArray()
        packet.append(f'uint:8={ProtocolSpec.SEND_PREFIX}')
        packet.append(f'hex:32={self.msg_seq}')
        packet.append(f'uint:8={unknown}')
        packet.append(f'uintle:16={body_len}')
        packet.append(f'uintle:16={body_len}')
        packet.append(f'hex:16={self.msg_type}')
        packet.append(self.msg_body)

        return packet.bytes

    def __bytes__(self) -> bytes:
        """让对象可以直接转换为 bytes"""
        return self.to_bytes()

    def to_hex(self, sep: str = " ") -> str:
        """调试用，返回十六进制字符串"""
        if sep == "":
            return self.to_bytes().hex().upper()
        return self.to_bytes().hex(sep).upper()

    def to_data(self):
        data_bytes = bytes(self)
        stream = ConstBitStream(data_bytes)

        msg_prefix = stream.read("hex:8")
        msg_seq = stream.read("hex:32")
        flag = stream.read("uint:8")
        body_len1 = stream.read("uintle:16")
        body_len2 = stream.read("uintle:16")
        msg_type = stream.read("hex:16")
        msg_body = stream.read(f"hex:{(body_len1 - 2) * 8}")

        return SendViewData(
            msg_prefix=msg_prefix,
            msg_seq=msg_seq,
            msg_type=msg_type,
            msg_body=msg_body,
        )
