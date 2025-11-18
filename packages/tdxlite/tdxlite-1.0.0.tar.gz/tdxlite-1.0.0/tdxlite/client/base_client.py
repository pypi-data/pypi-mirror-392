import socket
import select
from typing import Callable, TYPE_CHECKING
import zlib

from bitstring import ConstBitStream

from ..constants import ProtocolSpec
from ..models import RespViewData
from ..req import BaseReq
from ..parse import BaseParse


class BaseClient:

    def __init__(self, output: Callable = print, is_verbose: bool = False):
        self.output = output
        self.is_verbose = is_verbose

        self.client = None

        self.base_parse = BaseParse()

        # 存储 msg_seq -> 请求上下文
        self.req_context: dict[str, BaseReq] = {}

    def connect(self, ip: str, port: int, timeout: float = 10.0):
        self.client = socket.create_connection((ip, port), timeout=timeout)
        return self

    def close(self):
        try:
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
            self.client = None
        except Exception as e:
            self.output(fr"断开连接失败：{e}")
            self.client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def send(self, req: BaseReq):
        """发送请求"""
        # 将请求对象转换为字节数据
        req_bytes = bytes(req)

        # 存储请求上下文信息
        self.req_context[req.msg_seq] = req

        if self.is_verbose:
            self.output(fr"发送数据：{req_bytes.hex()}")

        # 发送数据
        self.client.sendall(req_bytes)

    def recv(self, size: int) -> bytes:
        """接收指定长度的数据"""
        recv_bytes = b''

        while len(recv_bytes) < size:
            chunk = self.client.recv(size - len(recv_bytes))
            if not chunk:
                raise ConnectionError("连接已关闭，数据接收中断")
            recv_bytes += chunk

        return recv_bytes

    def __parse_recv_header(self) -> RespViewData:
        """读取并解析响应头，获取响应体长度"""

        # 读取响应头
        header = self.recv(ProtocolSpec.RECV_HEADER_LEN)

        if self.is_verbose:
            self.output(fr"接收数据：{header.hex()}")

        # 解析响应头
        stream = ConstBitStream(header)
        msg_prefix = stream.read("hex:32")
        compressed_flag = stream.read("uintle:8")  # 压缩标记
        msg_seq = stream.read("hex:32")  # msg_seq
        _ = stream.read("bytes:1")  # unknown
        msg_type = stream.read("hex:16")
        compressed_size = stream.read("uintle:16")
        uncompressed_size = stream.read("uintle:16")

        return RespViewData(
            msg_prefix=msg_prefix,
            compressed_flag=compressed_flag,
            msg_seq=msg_seq,
            msg_type=msg_type,
            recv_len=compressed_size,
            body_len=uncompressed_size,
            is_verbose=self.is_verbose
        )

    def parse_recv(self):

        # 获取响应体长度
        resp_data: RespViewData = self.__parse_recv_header()

        # 读取响应体
        msg_body = self.recv(resp_data.recv_len)

        if resp_data.is_need_uncompress:
            msg_body = zlib.decompress(msg_body)

        resp_data.msg_body = msg_body

        req = self.req_context.pop(resp_data.msg_seq, None)
        resp_data.req = req  # 动态附加请求引用

        if self.is_verbose:
            print(fr"接收数据: {msg_body.hex()}")

        return self.base_parse.parse_body(resp_data)

    def send_and_parse_recv(self, req: BaseReq):
        self.send(req)
        return self.parse_recv()
