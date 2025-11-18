from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING, Optional, Callable
from datetime import time as Time, datetime as Datetime, timedelta

from bitstring import ConstBitStream

from ..constants import MsgType, ProtocolSpec

if TYPE_CHECKING:
    from ..req import BaseReq


class DataParse:

    def __init__(self, data: bytes, is_verbose: bool = False):
        self.data = data
        self.stream = ConstBitStream(data)
        self.is_verbose = is_verbose

        self.raw_value = None
        self.handled_value = None

        self._description = ""  # 用于存储字段描述
        self._start_pos = 0  # 记录读取开始位置

        self.trace_log_list = []  # 记录解析轨迹

    def read(self, fmt: str):
        self._start_pos = self.stream.pos  # 记录开始位置
        self.current_value = self.stream.read(fmt)
        return self

    def div(self, divisor: int | float):
        """缩小 divisor 倍"""
        self.current_value = self.current_value / divisor
        return self

    def mul(self, multiplier: int | float):
        """放大 multiplier 倍"""
        self.current_value = self.current_value * multiplier
        return self

    def as_date(self):
        """解析整数日期"""
        dt_int = self.current_value
        year = dt_int // 10000
        month = (dt_int % 10000) // 100
        day = dt_int % 100

        self.current_value = Datetime(year=year, month=month, day=day)
        return self

    def as_time_hm(self):
        total_min = self.current_value
        hour = total_min // 60
        minute = total_min % 60

        self.current_value = Time(hour=hour, minute=minute)
        return self

    def as_date_and_time_hm(self):
        ...

    def as_price(self):
        """变长整数"""
        b0 = self.current_value
        sign = -1 if (b0 & 0x40) else 1
        value = b0 & 0x3F
        shift = 6

        # 逐个追加后续字节
        while b0 & 0x80:
            b = self.stream.read('uint:8')
            value += (b & 0x7F) << shift
            shift += 7
            b0 = b

        self.current_value = sign * value

        return self

    def as_volume(self):
        ivol = self.current_value
        # 提取各个字节
        logpoint = ivol >> (8 * 3)  # 最高字节
        hleax = (ivol >> (8 * 2)) & 0xff  # 次高字节
        lheax = (ivol >> 8) & 0xff  # 第三字节
        lleax = ivol & 0xff  # 最低字节

        # 计算指数
        dwEcx = logpoint * 2 - 0x7f
        dwEdx = logpoint * 2 - 0x86
        dwEsi = logpoint * 2 - 0x8e
        dwEax = logpoint * 2 - 0x96

        # 计算第一个分量
        if dwEcx < 0:
            tmpEax = -dwEcx
            dbl_xmm6 = 1.0 / (2.0 ** tmpEax)
        else:
            dbl_xmm6 = 2.0 ** dwEcx

        # 计算第二个分量
        dbl_xmm4 = 0.0
        if hleax > 0x80:
            dwtmpeax = dwEdx + 1
            tmpdbl_xmm3 = 2.0 ** dwtmpeax
            dbl_xmm0 = (2.0 ** dwEdx) * 128.0
            dbl_xmm0 += (hleax & 0x7f) * tmpdbl_xmm3
            dbl_xmm4 = dbl_xmm0
        else:
            if dwEdx >= 0:
                dbl_xmm0 = (2.0 ** dwEdx) * hleax
            else:
                dbl_xmm0 = (1.0 / (2.0 ** -dwEdx)) * hleax
            dbl_xmm4 = dbl_xmm0

        # 计算第三和第四个分量
        dbl_xmm3 = (2.0 ** dwEsi) * lheax
        dbl_xmm1 = (2.0 ** dwEax) * lleax

        # 如果hleax的最高位为1，则加倍
        if hleax & 0x80:
            dbl_xmm3 *= 2.0
            dbl_xmm1 *= 2.0

        # 合并所有分量
        dbl_ret = dbl_xmm6 + dbl_xmm4 + dbl_xmm3 + dbl_xmm1

        self.current_value = dbl_ret
        return self

    def as_code(self):
        """解析为股票代码"""
        self.current_value = self.current_value.decode("utf-8", errors="ignore")
        return self

    def as_str(self):
        """解析字符串"""
        self.current_value = self.current_value.decode("gbk", errors="ignore").rstrip('\x00')
        return self

    def as_add(self, base_price: float):
        self.current_value = self.current_value + base_price
        return self

    def as_server_time(self):
        time_int = self.current_value
        if time_int == 0:
            return Time(hour=0, minute=0, second=0, microsecond=0)

        s = f"{time_int:09d}"  # 确保补足位数
        hour = int(s[0:2])
        minute = int(s[2:4])
        second = int(s[4:6])
        microsecond = int(s[6:9]) * 1000  # 毫秒→微秒

        # 校正合法范围
        hour = min(max(hour, 0), 23)
        minute = min(max(minute, 0), 59)
        second = min(max(second, 0), 59)

        self.current_value = Time(hour, minute, second, microsecond)
        return self

    def desc(self, description: str):
        """设置字段描述"""
        self._description = description
        return self

    def value(self):

        if not self.is_verbose:  # 非verbose模式直接返回
            return self.current_value

        if self._description:
            hex_str = self.get_hex_field()
            byte_length = len(hex_str) // 2 if hex_str else 0

            self.trace_log_list.append({
                "desc": self._description,
                "len": byte_length,
                "hex": hex_str,
                "value": self.current_value,
            })

            print(f"[字段解析]{self._description}: len={byte_length} | hex={hex_str} | value={self.current_value}")

        return self.current_value

    def apply(self, func: Callable):
        """扩展性"""
        self.current_value = func(self.current_value)
        return self

    def get_hex_field(self):
        """获取读取字节的十六进制表示"""
        byte_length = (self.stream.pos - self._start_pos) // 8
        if byte_length > 0:
            # 回退到开始位置读取原始字节
            current_pos = self.stream.pos
            self.stream.pos = self._start_pos
            raw_bytes = self.stream.read(f'bytes:{byte_length}')
            self.stream.pos = current_pos
            return raw_bytes.hex()
        return ""

    def trace_log(self) -> str:
        """拼接完整解析轨迹字符串"""
        if not self.is_verbose or not self.trace_log_list:
            return ""
        parts = []
        for item in self.trace_log_list:
            val = item["value"]
            if isinstance(val, bytes):
                try:
                    val_str = val.decode("utf-8", "ignore")
                except:
                    val_str = val.hex()
            else:
                val_str = str(val)
            parts.append(f"{item['hex']}[{item['desc']}->{val_str}]")
        return "-".join(parts)


@dataclass
class RespViewData:
    """响应视图数据对象"""

    msg_prefix: str
    compressed_flag: int
    msg_seq: str
    msg_type: MsgType
    recv_len: int  # 接收长度
    body_len: int  # 消息体长度，即解压后的消息体长度
    msg_body: bytes = b""

    req: Optional["BaseReq"] = None

    _stream: DataParse | None = field(default=None, init=False, repr=False)

    is_verbose: bool = False

    @property
    def stream(self) -> DataParse:
        if self._stream is None:
            if not self.msg_body:
                raise Exception("msg_body 为空，无法创建 DataParse 实例")
            self._stream = DataParse(self.msg_body, is_verbose=self.is_verbose)

        return self._stream

    @property
    def is_need_uncompress(self):
        """为否需要解压"""
        return self.compressed_flag == ProtocolSpec.COMPRESSED_FLAG

    def __setattr__(self, name: str, value: Any) -> None:
        """允许动态设置 body_ 开头的扩展属性"""
        if name.startswith('body_') or name in self.__dataclass_fields__:  # noqa
            super().__setattr__(name, value)
        else:
            raise AttributeError(
                f"只允许设置 dataclass 字段或 body_ 开头的扩展属性，"
                f"不允许设置: {name}"
            )

    def get_body_info(self) -> dict:
        """获取所有以 body_ 开头的字段"""
        return {
            key: value
            for key, value in self.__dict__.items()
            if key.startswith('body_')
        }

    def get_compress_info(self) -> dict:
        """获取压缩相关信息"""
        return {
            "compressed_flag": hex(self.compressed_flag),
            "recv_len": self.recv_len,
            "expected_body_len": self.body_len,
            "actual_body_len": len(self.msg_body),
        }
