import threading
import itertools

_counter = itertools.count(1)
_lock = threading.Lock()


def get_msg_seq() -> str:
    """消息流水号：msg_seq"""
    with _lock:
        seq = next(_counter) & 0xFFFFFFFF
    return f"{seq:08x}"


if __name__ == '__main__':
    print(get_msg_seq())
    print(get_msg_seq())
