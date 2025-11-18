from typing import Callable
import zlib

from bitstring import ConstBitStream

from ..constants import MsgType
from ..models import SendViewData, RespViewData


class BaseParse:
    # 映射表：消息类型 -> 解析函数
    msg_type_maps: dict[MsgType, Callable] = {}

    @classmethod
    def register(cls, msg_type: MsgType):
        """装饰器：注册特定消息类型的解析器"""

        def decorator(handler_func: Callable):
            cls.msg_type_maps[msg_type] = handler_func
            return handler_func

        return decorator

    def parse_body(self, resp_data: RespViewData):
        msg_type = resp_data.msg_type

        # 匹配解析器
        if msg_type in self.msg_type_maps:
            return self.msg_type_maps[msg_type](resp_data)

        return resp_data

    def parse_send_data(self, send_data: bytes):
        stream = ConstBitStream(send_data)

        msg_prefix = stream.read("hex:8")
        msg_seq = stream.read("hex:32")
        unknown = stream.read("hex:8")
        body_len1 = stream.read("uintle:16")
        body_len2 = stream.read("uintle:16")
        msg_type = stream.read("hex:16")
        msg_body = stream.read(f"hex:{(body_len1 - 2) * 8}")

        return SendViewData(
            msg_prefix=msg_prefix,
            msg_seq=msg_seq,
            msg_type=msg_type,
            msg_body=msg_body
        )

    def parse_recv_data(self, recv_data: bytes):
        stream = ConstBitStream(recv_data)

        msg_prefix = stream.read("hex:32")
        compressed_flag = stream.read("uintle:8")  # 压缩标记
        msg_seq = stream.read("hex:32")  # msg_seq
        _ = stream.read("bytes:1")  # unknown
        msg_type = stream.read("hex:16")
        compressed_size = stream.read("uintle:16")
        uncompressed_size = stream.read("uintle:16")

        remaining_bytes = (len(stream) - stream.pos) // 8
        msg_body = stream.read(f"bytes:{remaining_bytes}")

        resp_data = RespViewData(
            msg_prefix=msg_prefix,
            compressed_flag=compressed_flag,
            msg_seq=msg_seq,
            msg_type=msg_type,
            recv_len=compressed_size,
            body_len=uncompressed_size,
            msg_body=msg_body
        )

        if resp_data.is_need_uncompress:
            try:
                msg_body = zlib.decompress(msg_body)
                resp_data.msg_body = msg_body
            except:
                print(fr"解压数据失败_数据长度对不上：{msg_type}")
                print(fr"完整数据: {recv_data.hex()}")
                print(fr"body: {msg_body.hex()}")
                print(fr"压缩信息：{resp_data.get_compress_info()}")

                return resp_data

        return self.parse_body(resp_data)
