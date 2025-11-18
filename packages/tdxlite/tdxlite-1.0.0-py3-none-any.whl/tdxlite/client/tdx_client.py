from typing import Callable, TYPE_CHECKING

import pandas as pd

from .base_client import BaseClient
from ..req import (
    BeatHeartReq, ShortMarketReq
)
from ..constants import Board

if TYPE_CHECKING:
    from ..req import BaseReq


class TdxClient(BaseClient):

    def __init__(self, ip: str | None = None, port: int | None = None, output: Callable = print,
                 is_verbose: bool = False):

        if ip is None:
            ip = '116.205.171.132'

        if port is None:
            port = 7709

        super().__init__(output=output, is_verbose=is_verbose)

        self.is_verbose = is_verbose

        if self.is_verbose:
            pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
            pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数

        self.connect(ip, port)

        self.bns_beat()

    def bns_beat(self):
        """发送心跳"""
        req: BaseReq = BeatHeartReq()
        self.send_and_parse_recv(req)

    def get_stock_list_bj(self):
        """获取北交所成分股"""

        PAGE_SIZE = 80
        PAGE_COUNT = 4

        all_dfs = []
        for i in range(PAGE_COUNT):
            req = ShortMarketReq(board=Board.BJ, start=i * PAGE_SIZE, count=PAGE_SIZE)
            resp_data = self.send_and_parse_recv(req)

            if getattr(resp_data, "body_data", None):
                all_dfs.append(pd.DataFrame(resp_data.body_data))

        df = pd.concat(all_dfs, ignore_index=True) if all_dfs else None

        return df["xt_symbol"].tolist()
