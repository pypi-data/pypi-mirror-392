class ProtocolSpec:
    """协议规格定义"""
    SEND_PREFIX = 0x0c
    RECV_PREFIX = b"\xb1\xcb\x74\x00"
    COMPRESSED_FLAG = 0x1c

    RECV_HEADER_LEN = 0x10  # 响应协议头长度
