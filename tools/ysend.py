#!/usr/bin/env python3
"""Minimal YMODEM sender (1K blocks, CRC16) for U-Boot's "loady".

Usage: ysend.py <tty> <file> [baud]
Start "loady <addr>" on the target first; it then prints 'C' while waiting.
"""
import os
import sys
import termios
import time

SOH, STX, EOT, ACK, NAK, CAN, CRC = 0x01, 0x02, 0x04, 0x06, 0x15, 0x18, 0x43


def crc16(data):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc


def open_tty(path, baud):
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY)
    attr = termios.tcgetattr(fd)
    attr[0] = 0                                  # iflag
    attr[1] = 0                                  # oflag
    attr[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    attr[3] = 0                                  # lflag
    speed = getattr(termios, "B%d" % baud)
    attr[4] = attr[5] = speed
    attr[6][termios.VMIN] = 0
    attr[6][termios.VTIME] = 1                   # 0.1 s read timeout
    termios.tcsetattr(fd, termios.TCSANOW, attr)
    termios.tcflush(fd, termios.TCIOFLUSH)
    return fd


def getc(fd, timeout):
    end = time.time() + timeout
    while time.time() < end:
        b = os.read(fd, 1)
        if b:
            return b[0]
    return None


def wait_for(fd, wanted, timeout):
    end = time.time() + timeout
    while time.time() < end:
        c = getc(fd, end - time.time())
        if c in wanted:
            return c
    return None


def send_block(fd, num, payload, size):
    payload = payload.ljust(size, b"\x1a" if num else b"\x00")
    head = bytes([STX if size == 1024 else SOH, num & 0xFF, 0xFF - (num & 0xFF)])
    crc = crc16(payload)
    pkt = head + payload + bytes([crc >> 8, crc & 0xFF])
    for _ in range(16):
        os.write(fd, pkt)
        c = wait_for(fd, (ACK, NAK, CAN), 5)
        if c == ACK:
            return True
        if c == CAN:
            sys.exit("receiver cancelled")
        # NAK, noise or timeout: drop stray input and resend
        time.sleep(0.1)
        termios.tcflush(fd, termios.TCIFLUSH)
    sys.exit("block %d failed 16 times" % num)


def main():
    tty, path = sys.argv[1], sys.argv[2]
    baud = int(sys.argv[3]) if len(sys.argv) > 3 else 115200
    data = open(path, "rb").read()
    fd = open_tty(tty, baud)

    if wait_for(fd, (CRC,), 30) is None:
        sys.exit("no 'C' from receiver (is loady running?)")

    name = os.path.basename(path).encode()
    send_block(fd, 0, name + b"\0" + str(len(data)).encode() + b"\0", 128)
    wait_for(fd, (CRC,), 10)

    total = (len(data) + 1023) // 1024
    for i in range(total):
        send_block(fd, (i + 1) & 0xFF, data[i * 1024:(i + 1) * 1024], 1024)
        if i % 64 == 0 or i == total - 1:
            print("\r%3d%%" % (100 * (i + 1) // total), end="", flush=True)
    print()

    for _ in range(10):
        os.write(fd, bytes([EOT]))
        if wait_for(fd, (ACK, NAK), 5) == ACK:
            break
    wait_for(fd, (CRC,), 5)
    send_block(fd, 0, b"", 128)                  # empty block 0: end of batch
    print("sent %d bytes" % len(data))


if __name__ == "__main__":
    main()
