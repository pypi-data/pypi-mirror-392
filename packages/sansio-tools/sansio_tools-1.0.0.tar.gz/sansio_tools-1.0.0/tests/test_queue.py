import itertools
import re

import pytest

from sansio_tools.queue import BytesQueue, StringQueue, NeedMoreItemsError, FileAdapterFromGeneratorBytes


def test_string_queue():
    q = StringQueue()

    q.append("0123")
    assert len(q) == 4

    assert str(q.popleft(1)) == "0"
    assert str(q.popleft(1)) == "1"

    q.appendleft("ab")
    assert q.popleft(4) == "ab23"


def _s(q: BytesQueue):
    r = b"".join(q.data)
    assert r == bytes(q)
    return r


def _a(q: BytesQueue):
    xs = [bytes(x) for x in q.iter_blocks()]
    assert len(q) == sum(len(x) for x in xs)
    return xs


def test_queue_popleft():
    q = BytesQueue((b"012", b"345"))
    assert bytes(q.popleft(1)) == b"0"
    assert _a(q) == [b"12", b"345"]
    assert bytes(q.popleft(3)) == b"123"
    assert _a(q) == [b"45"]


def test_queue_pop():
    q = BytesQueue((b"012", b"345"))
    assert bytes(q.pop(1)) == b"5"
    assert _a(q) == [b"012", b"34"]
    assert bytes(q.pop(3)) == b"234"
    assert _a(q) == [b"01"]


def test_queue_pop_to():
    q = BytesQueue((b"012", b"345"))
    q2 = BytesQueue()
    q.pop_to(1, q2)
    assert _a(q) == [b"012", b"34"]
    assert _a(q2) == [b"5"]
    q.pop_to(4, q2)
    assert _a(q) == [b"0"]
    assert _a(q2) == [b"12", b"34", b"5"]


def test_queue_popleft_to():
    q = BytesQueue((b"012", b"345"))
    q2 = BytesQueue()
    q.popleft_to(1, q2)
    assert _a(q) == [b"12", b"345"]
    assert _a(q2) == [b"0"]
    q.popleft_to(4, q2)
    assert _a(q) == [b"5"]
    assert _a(q2) == [b"0", b"12", b"34"]


@pytest.mark.parametrize("exception", [False, True])
def test_queue_temporary_left(exception):
    q = BytesQueue((b"012", b"345"))
    try:
        with q.temporary_left() as tmp:
            q.popleft_to(4, tmp)
            assert _a(tmp) == [b"012", b"3"]
            tmp.pop(1)
            tmp.popleft(1)
            assert _a(tmp) == [b"12"]
            assert _a(q) == [b"45"]
            if exception:
                raise RuntimeError
    except RuntimeError:
        pass
    assert _a(q) == [b"12", b"45"]
    assert _a(tmp) == []


def test_queue_iter_blocks():
    q = StringQueue()
    q.append("234")
    q.appendleft("01")
    q.append("56")
    assert list(q.iter_blocks()) == ["01", "234", "56"]

    assert q.peekleft(3) == "012"
    assert q.peek(3) == "456"
    assert list(q.iter_blocks()) == ["012", "3", "456"]
    assert q.peek_any() == "456"


def test_queue_popleft():
    q = StringQueue()
    q.append("0")
    assert q.popleft_any() == "0"
    assert q.popleft_any() is None
    assert q.peekleft_any() is None
    assert q.peek_any() is None


def test_queue_pop_to():
    q = StringQueue()
    q2 = StringQueue()
    q.append("012")

    q.popleft_to(1, q2)
    assert str(q) == "12"
    assert str(q2) == "0"

    with pytest.raises(NeedMoreItemsError):
        q.popleft_to(3, q2)

    with pytest.raises(NeedMoreItemsError):
        q.popleft(3)

    q.popleft_to(2, q2)
    assert not q
    assert str(q2) == "012"

    q.swap(q2)

    q.pop_to(1, q2)
    assert str(q) == "01"
    assert str(q2) == "2"

    with pytest.raises(NeedMoreItemsError):
        q.pop_to(3, q2)

    with pytest.raises(NeedMoreItemsError):
        q.pop(3)

    q.pop_to(2, q2)
    assert not q
    assert str(q2) == "012"


def test_popleft_all_to():
    q1 = StringQueue(["01", "23"])
    q2 = StringQueue(["45", "67"])

    q1.popleft_all_to(q2)
    assert not q1
    assert list(q2.iter_blocks()) == ["45", "67", "01", "23"]


def test_pop_all_to():
    q1 = StringQueue(["01", "23"])
    q2 = StringQueue(["45", "67"])

    q1.pop_all_to(q2)
    assert not q1
    assert list(q2.iter_blocks()) == ["01", "23", "45", "67"]


def test_queue_peek():
    q = StringQueue(["012"])
    assert q.peek(4) is None
    assert q.peekleft(4) is None
    assert q.peek(2) == "12"
    assert q.peekleft(2) == "01"
    assert q.peek(3) == "012"
    assert q.peekleft(3) == "012"


def test_queue_copy():
    q = StringQueue(["012"])
    q2 = q.copy()
    q2.clear()
    assert str(q) == "012"
    assert str(q2) == ""
    assert q.contents == "012"


def test_bytes_queue():
    q = BytesQueue()
    assert len(q) == 0
    assert not q

    q.append(b"0123")
    assert len(q) == 4
    assert bool(q)

    q.append(b"456")
    assert len(q) == 7
    assert _s(q) == b"0123456"

    assert bytes(q.peekleft(1)) == b"0"
    assert len(q.peekleft_any()) == 1
    assert bytes(q.peekleft(3)) == b"012"
    assert len(q.peekleft_any()) == 3

    assert bytes(q.popleft(2)) == b"01"
    assert len(q) == 5
    assert _s(q) == b"23456"

    q.appendleft(b"ab")
    assert len(q) == 7
    assert _s(q) == b"ab23456"

    assert bytes(q.peekleft(4)) == b"ab23"

    assert bytes(q.popleft_any()) == b"ab23"
    assert len(q) == 3
    assert _s(q) == b"456"

    with q.popleft_after(2) as b:
        assert bytes(b) == b"45"
        assert len(q) == 3
        assert _s(q) == b"456"
    assert len(q) == 1
    assert _s(q) == b"6"

    q.append(b"789")
    assert len(q) == 4
    assert _s(q) == b"6789"

    try:
        with q.popleft_after(2) as b:
            assert bytes(b) == b"67"
            assert len(q) == 4
            raise RuntimeError
    except RuntimeError:
        pass
    assert len(q) == 4

    with pytest.raises(NeedMoreItemsError):
        q.popleft(5)

    with pytest.raises(NeedMoreItemsError):
        with q.popleft_after(5) as b:
            pass

    assert len(q) == 4


_test_file_adapter_from_generator_strategies = {
    "1": [1],
    "3": [3],
    "1_9": [1, 9],
    "1_4": [1, 4],
    "3_5_1_1": [3, 5, 1, 1],
    "20": [20],
}


@pytest.mark.parametrize("N", [1, 7, 10])
@pytest.mark.parametrize("sizes_strategy", _test_file_adapter_from_generator_strategies.keys())
def test_file_generator_basic_read(sizes_strategy, N):
    sizes = itertools.cycle(_test_file_adapter_from_generator_strategies[sizes_strategy])

    def _gen(n):
        for _ in range(n):
            yield b"012"
            yield bytearray(b"34567")
            yield None
            yield memoryview(b"89")

    f = FileAdapterFromGeneratorBytes(_gen(N))
    out = []
    count = 0
    while True:
        block = f.read()
        if block == b"":
            break
        count += len(block)
        out.append(block)

    assert count == 10 * N
    assert b"".join(out) == b"0123456789" * N
    assert re.compile(r"^FileAdapter.*\(_generator=<.*>, _buffered_count=0, closed=False\)$").search(repr(f))
    f.close()
    assert re.compile(r"^FileAdapter.*\(_generator=<.*>, _buffered_count=0, closed=True\)$").search(repr(f))


def test_file_generator_cancel():
    EXC = []

    def _gen():
        yield b"01"
        try:
            yield b"23"
        except BaseException as exc:
            EXC.append(exc)
            raise
        assert False

    f = FileAdapterFromGeneratorBytes(_gen())
    assert f.readable() and not f.writable() and not f.seekable()
    assert f.read(2) == b"01"
    assert f.read(2) == b"23"
    f.close()
    assert EXC and isinstance(EXC[0], GeneratorExit)
    EXC.clear()
    f.close()
    assert not EXC
