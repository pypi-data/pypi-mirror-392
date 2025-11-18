import re
from enum import Enum
from typing import NamedTuple
from functools import cache


class ExchangeInfo(NamedTuple):
    int_code: int
    str_code: str


exchange_code_prefix_map = {
    "SH": ("6", "51", "50", "11", "56", "58", "52", "53", "55"),
    "SZ": ("0", "3", "15", "16", "12", "18"),
    "BJ": ("4", "8", "9"),
}


class Exchange(Enum):
    SH = ExchangeInfo(1, "SH")
    SZ = ExchangeInfo(0, "SZ")
    BJ = ExchangeInfo(2, "BJ")

    def __repr__(self):
        return self.value.str_code

    @property
    def int_code(self):
        return self.value.int_code

    @property
    def str_code(self):
        return self.value.str_code

    @classmethod
    def int2str(cls, code: int) -> str:
        for ex in cls:
            if ex.int_code == code:
                return ex.str_code
        raise ValueError(f"未知交易所整数标识: {code}")

    @classmethod
    def str2int(cls, s: str) -> int:
        for ex in cls:
            if ex.str_code == s:
                return ex.int_code
        raise ValueError(f"未知交易所字符串标识: {s}")

    @classmethod
    def from_str(cls, s: str) -> "Exchange":
        """根据[字符串代码]，返回对应的[Exchang对象]"""
        s = s.strip().upper()
        try:
            return cls[s]
        except KeyError:
            raise ValueError(f"未知交易所字符串标识: {s}")

    @classmethod
    @cache
    def infer_exchange(cls, code: str) -> "Exchange":
        """
        根据[code]来推断出所属交易所[exchange]
        :param code: 标的代码
        :return:
        """
        code = code.strip()

        match = re.search(pattern=r"^\d{6}$", string=code)
        if not match:
            raise Exception(fr"symbol格式不正确:{code}，应为6位数字代码")

        trade_code = match.group(0)

        for ex_name, prefixes in exchange_code_prefix_map.items():
            if trade_code.startswith(prefixes):
                return cls[ex_name]

        raise ValueError(f"无法识别的交易代码：{code}")


if __name__ == '__main__':
    print(Exchange.SH)
    print(Exchange.BJ.int_code)

    print(Exchange.int2str(2))

    print(Exchange.str2int("SH"))

    print(Exchange["SH"])

    print(Exchange.infer_exchange("600100"))
    print(Exchange.infer_exchange("150100") == Exchange.SZ)

    print(Exchange.from_str("SH"))
