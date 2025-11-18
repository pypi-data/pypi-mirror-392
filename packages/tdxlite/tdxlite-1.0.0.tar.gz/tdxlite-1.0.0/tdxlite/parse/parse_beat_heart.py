from datetime import datetime as Datetime

from bitstring import ConstBitStream

from .base_parse import BaseParse
from ..models import RespViewData
from ..constants import MsgType


@BaseParse.register(MsgType.beat_heart)
def parse_beat_heart(resp_data: RespViewData):
    stream = ConstBitStream(resp_data.msg_body)

    _ = stream.read('uintle:8')  # B
    year = stream.read('uintle:16')  # H
    day = stream.read('uintle:8')  # B
    month = stream.read('uintle:8')  # B
    minute = stream.read('uintle:8')  # B
    hour = stream.read('uintle:8')  # B
    _ = stream.read('uintle:8')  # B
    second = stream.read('uintle:8')  # B

    date = stream.read("uintle:32")  # I
    a1 = stream.read("uintle:16")  # H
    b1 = stream.read("uintle:16")  # H
    date2 = stream.read("uintle:32")  # I
    a2 = stream.read("uintle:16")  # H
    b2 = stream.read("uintle:16")  # H

    unknown4 = stream.read("uintle:16")  # H
    unknown5 = stream.read("uintle:16")  # H
    unknown6 = stream.read("bytes:5")  # 5s

    server_name = stream.read("bytes:22")  # 22s
    web_site = stream.read("bytes:64")  # 64s
    unknown7 = stream.read("bytes:6")  # 6s
    category = stream.read("bytes:30")  # 30s

    stream.read("bytes:15")

    date_time = Datetime(year, month, day, hour, minute, second)
    resp_data.body_date_time = date_time

    resp_data.body_server_name = server_name

    return resp_data
