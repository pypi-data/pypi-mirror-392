from contextlib import nullcontext
import re
import struct

import pytest

from sansio_tools.parser import BinaryParser, UnexpectedEOFError, TrailingDataError
from sansio_tools.queue import FileAdapterFromGeneratorBytes


def test_parse_no_generator():
    with pytest.raises(AssertionError):
        p = BinaryParser()
        p.feed(None)


def test_parse_simple():
    struct_two_u16be = struct.Struct("!HH")

    results = []

    def gen(p: BinaryParser):
        r = yield from p.read_struct(struct_two_u16be)
        results.append(r)

        b = yield from p.read_bytes(6)
        results.append(b)

        n = yield from p.read_int(2, "little", False)
        results.append(n)

    p = BinaryParser(gen, trailing_data_raises=False)
    assert len(results) == 0

    p.feed(b"\x04\x00\x00\x01")
    assert len(results) == 1
    assert results[0] == (1024, 1)

    p.feed(b"01234")
    assert len(results) == 1

    p.feed(b"5\x07")
    assert len(results) == 2
    assert results[1] == b"012345"
    assert not p.generator_exited

    p.feed(b"\xffex")
    assert len(results) == 3
    assert p.generator_exited
    assert len(p.queue) == 2

    p.feed(b"tra")
    assert len(p.queue) == 5
    assert not p.eof

    p.feed(None)
    assert p.eof
    assert len(p.queue) == 5

    with pytest.raises(ValueError, match="eof"):
        p.feed(b"invalid write after end of stream")


def test_parse_varint_special():
    def _f(data, bo, cbit, canon):
        def parser(p: BinaryParser):
            n1 = yield from p.read_variable_length_int_7bit(
                9, byteorder=bo, continuation_bit_value=cbit, require_canonical=canon
            )
            results.append(n1)

        p = BinaryParser(parser)
        results = []
        p.feed(data)
        return results[0]

    assert _f(b"\x82\x03", bo="big", cbit=True, canon=True) == 256 + 3
    assert _f(b"\x02\x83", bo="big", cbit=False, canon=True) == 256 + 3

    assert _f(b"\x80\x03", bo="big", cbit=True, canon=False) == 3
    with pytest.raises(ValueError, match="canonical"):
        _f(b"\x80\x03", bo="big", cbit=True, canon=True)

    assert _f(b"\x83\x00", bo="little", cbit=True, canon=False) == 3
    with pytest.raises(ValueError, match="canonical"):
        _f(b"\x83\x00", bo="little", cbit=True, canon=True)


@pytest.mark.parametrize("n", {o + 2**k for o in {-1, 0, 1} for k in (0, 7, 14, 21)})
@pytest.mark.parametrize("byteorder", ["little", "big"])
@pytest.mark.parametrize("split", [True, False])
def test_parse_varint(n, byteorder, split):
    N = n
    r = []
    while True:
        r.append(n & 127)
        n >>= 7
        if not n:
            break
    if byteorder == "big":
        r.reverse()
    for i in range(len(r) - 1):
        r[i] = r[i] | 128

    parser_results = []
    feed_input = bytes(r) + b"\xff"

    def parser(p: BinaryParser):
        n1 = yield from p.read_variable_length_int_7bit(
            2, byteorder, continuation_bit_value=True, require_canonical=True
        )
        parser_results.append(n1)

    def feed():
        if split:
            for i in range(len(feed_input)):
                p.feed(feed_input[i : i + 1])
        else:
            p.feed(feed_input)

    p = BinaryParser(parser, trailing_data_raises=False)
    if N >= 2**14:
        with pytest.raises(ValueError):
            feed()
        if split:
            expected_queue = feed_input[:2]
        else:
            expected_queue = feed_input
        assert not parser_results
    else:
        feed()
        expected_queue = feed_input[-1:]
        assert parser_results[0] == N

    assert b"".join(p.queue.data) == expected_queue


@pytest.mark.parametrize("i,j", [(i, j) for i in range(1, 8) for j in range(i + 1, 8 + 1)])
@pytest.mark.parametrize("exception", [False, True])
def test_parse_one(i, j, exception):
    data = memoryview(bytearray(b"01234567"))
    if exception:
        data[0] = 0
    results = []

    def parser(p: BinaryParser):
        results.append(x := (yield from p.read_bytes(5)))
        if x[0] == 0:
            print(1 // 0)
        results.append((yield from p.read_bytes(3)))

    p = BinaryParser(parser)
    with pytest.raises(ZeroDivisionError) if exception and (j >= 5) else nullcontext():
        p.feed(data[:i])
        p.feed(data[i:j])

    if not exception:
        if j == 8:
            p.feed(None)
            assert len(results) == 2
        else:
            with pytest.raises(UnexpectedEOFError):
                p.feed(None)


@pytest.mark.parametrize("feed_from", ["bytes", "iter", "file"])
def test_parse_misc(feed_from):
    struc = struct.Struct("!HHH")
    out = []

    input_blocks = [b"0", b"12", b"345", b"678"]

    def _data_gen():
        yield from input_blocks

    def parser(p: BinaryParser):
        out.append((yield from p.read_bytes(3)))
        out.append((yield from p.read_bytes(1)))
        out.append((yield from p.read_bytes(5)))

    p = BinaryParser(parser)
    assert p.generator is not None

    if feed_from == "bytes":
        p.feed(b"".join(input_blocks)).feed(None)
    elif feed_from == "iter":
        p.feed_from_iter(iter(input_blocks))
    elif feed_from == "file":
        p.feed_from_file(FileAdapterFromGeneratorBytes(_data_gen()))
    else:
        raise AssertionError

    assert out == [b"012", b"3", b"45678"]
    assert re.compile(
        r"^BinaryParser\(generator=<.*>, position=9, buffered_count=0, eof=True, trailing_data_raises=True\)$"
    ).search(repr(p))


@pytest.mark.parametrize("n", range(5))
def test_parser_trailing(n):
    def parser(p: BinaryParser):
        yield from p.read_bytes(2)

    p = BinaryParser(parser)
    if n < 2:
        if n:
            p.feed(b"x" * n)
        with pytest.raises(UnexpectedEOFError):
            p.feed(None)
    elif n == 2:
        p.feed(b"x" * n)
        p.feed(None)
    elif n > 2:
        with pytest.raises(TrailingDataError):
            p.feed(b"x" * n)


def test_parser_stupid():
    def _gen(p: BinaryParser):
        n = yield from p.read_variable_length_int_7bit(2, "foobar", True, False)

    p = BinaryParser(_gen)
    with pytest.raises(ValueError, match="byteorder"):
        p.feed(b"0123")
