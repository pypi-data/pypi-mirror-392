from .base_parse import BaseParse
from ..models import RespViewData
from ..constants import MsgType, Exchange


@BaseParse.register(MsgType.short_market)
def parse_short_market(resp_data: RespViewData):
    stream = resp_data.stream
    price_tick_map = getattr(resp_data.req, "price_tick_map", {})

    stream.read("bytes:2").desc("预留字段")
    count = stream.read("uintle:16").desc("记录数量").value()

    ticks = []

    for _ in range(count):
        exchange_str = stream.read("uintle:8").desc("交易所代码").value()
        stock_code = stream.read("bytes:6").as_code().desc("股票代码").value()

        xt_symbol = fr"{stock_code}.{Exchange.int2str(exchange_str)}"
        price_tick = price_tick_map.get(xt_symbol, 0.01)

        activity = stream.read("uintle:16").desc("活跃度").value()
        latest_price_raw = stream.read("uintle:8").as_price().desc("最新价格").value()
        latest_price = latest_price_raw * price_tick

        last_close = stream.read("uintle:8").as_price().as_add(latest_price_raw).mul(price_tick).desc(
            "前收盘价").value()
        open_ = stream.read("uintle:8").as_price().as_add(latest_price_raw).mul(price_tick).desc("开盘价").value()
        high = stream.read("uintle:8").as_price().as_add(latest_price_raw).mul(price_tick).desc("最高价").value()
        low = stream.read("uintle:8").as_price().as_add(latest_price_raw).mul(price_tick).desc("最低价").value()
        server_time = stream.read("uintle:8").as_price().as_server_time().desc("服务器时间").value()
        after_volumn = stream.read("uintle:8").as_price().desc("盘后成交量").value()
        volumn = stream.read("uintle:8").as_price().desc("成交量").value()
        cur_vol = stream.read("uintle:8").as_price().desc("cur_vol未解析").value()
        turnover = stream.read("floatle:32").desc("成交额").value()
        inner_volume = stream.read("uintle:8").as_price().desc("内盘").value()
        outer_volume = stream.read("uintle:8").as_price().desc("外盘").value()
        s_amount = stream.read("uintle:8").as_price().desc("s_amount未解析").value()
        b_amount = stream.read("uintle:8").as_price().desc("b_amount未解析").value()

        # 1档盘口
        bid_price_1 = stream.read("uintle:8").as_price().as_add(latest_price_raw).mul(price_tick).desc("买1").value()
        ask_price_1 = stream.read("uintle:8").as_price().as_add(latest_price_raw).mul(price_tick).desc("卖1").value()
        bid_volume_1 = stream.read("uintle:8").as_price().desc("买1量").value()
        ask_volume_1 = stream.read("uintle:8").as_price().desc("卖1量").value()

        # 未知字段
        v1 = stream.read("uintle:16").desc("v1未解析").value()
        change_speed = stream.read("intle:16").div(100.0).desc("涨速").value()

        unknown1 = stream.read("bytes:8").desc("unknown1")
        stream.read("bytes:10").desc("预留字段")
        unknown2 = stream.read("bytes:8").desc("unknown2")
        stream.read("bytes:24").desc("预留字段")

        activity2 = stream.read("uintle:16").desc("活跃度_重复字段").value()

        ticks.append({
            "xt_symbol": xt_symbol,
            "latest": latest_price,
            "open": open_,
            "high": high,
            "low": low,
            "last_close": last_close,
            "server_time": server_time,
            "after_volumn": after_volumn,
            "volumn": volumn,
            "turnover": turnover,
            "inner_volume": inner_volume,
            "outer_volume": outer_volume,
            "change_speed": change_speed / 100.0,
            "activity": activity,

            "bid_price_1": bid_price_1,
            "ask_price_1": ask_price_1,
            "bid_volume_1": bid_volume_1,
            "ask_volume_1": ask_volume_1,
        })

    resp_data.body_data = ticks

    return resp_data
