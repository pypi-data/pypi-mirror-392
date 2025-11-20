# sansio_tools

Useful tools for building [Sans IO](https://sans-io.readthedocs.io/)-based libraries.

## BytesQueue

Example code:

```python
from sansio_tools.queue import BytesQueue

q = BytesQueue()

q.append(b"012345")

print(bytes(q.peekleft(2)))  # b"01"

print(bytes(q.popleft(3)))  # b"012"

# put the bytes back into the queue!
q.appendleft(b"012")

print(bytes(q.popleft(4)))  # b"0123"
```

## Parser and BytesParser

Example code:

```python
from struct import Struct
from sansio_tools.parser import BinaryParser


# int8, uint32, uint64
my_struct = Struct("!bIQ")

def parser_generator(p: BinaryParser):
    b = yield from p.read_bytes(6)
    results.append(b)
    b = yield from p.read_bytes(6)
    results.append(b)

    lst = yield from p.read_struct(my_struct)
    results.append(lst)

    n = yield from p.read_int(2, "little", False)
    results.append(n)

    n = yield from p.read_variable_length_int_7bit(
        maximum_length=10,
        byteorder="big",
        continuation_bit_value=True,
        require_canonical=True,
    )
    results.append(n)

results = []
p = BinaryParser(parser_generator)
p.feed(b"hell")
p.feed(b"o world!\xff")

# receive partial results as they become available!
assert results == [b"hello ", b"world!"]
assert not p.generator_exited
results.clear()

p.feed(b"\xff\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x12\x34")
p.feed(b"\x81\x80\x80")

assert results == [(-1, 0xff << 24, 0xff << 56), 0x3412]
assert not p.generator_exited
results.clear()

p.feed(b"\x80\x05")
p.feed(b"")  # signal eof

assert results == [(1 << (7 * 4)) + 5]
assert p.generator_exited
```
