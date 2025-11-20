from __future__ import annotations

import abc
import struct as _struct
import typing as ty

from .queue import SolidQueue, BytesQueue

from ._util import repr_helper


class UnexpectedEOFError(ValueError):
    """
    Raised if the input stream ends while the parser is expecting more data.
    """


class TrailingDataError(ValueError):
    """
    Raised if there is unparsed data at the end and :attr:`Parser.trailing_data_raises` is false.
    """


def _complain(p):
    raise AssertionError(f"you must set `{str(type(p).__name__)}.generator`")
    yield


T = ty.TypeVar("T")


class Parser(ty.Generic[T]):
    queue: SolidQueue[T]
    position: int = 0
    eof: bool = False
    generator_exited: bool = False
    trailing_data_raises: bool = True

    def _repr_attribs(self):
        return dict(
            generator=self.generator,
            position=self.position,
            buffered_count=self.buffered_count,
            eof=self.eof,
            trailing_data_raises=self.trailing_data_raises,
        )

    def __repr__(self):
        return repr_helper(self, self._repr_attribs())

    @property
    def buffered_count(self) -> int:
        return len(self.queue)

    def __init__(
        self,
        generator: ty.Callable[[Parser[T]], ty.Generator[bool | None, None, None]] = None,
        trailing_data_raises: bool = True,
    ):
        if generator is None:
            generator = _complain
        self.generator = generator(self)
        self.trailing_data_raises = trailing_data_raises
        self._init_queue()

    @abc.abstractmethod
    def _init_queue(self): ...

    def feed_without_parsing(self, data: T | None) -> None:
        if data is None:
            self.eof = True
        else:
            if self.eof:
                raise ValueError("cannot feed data if eof=True")
            self.queue.append(data)

    def feed(self, data: T | None):
        """
        Add *data* to the internal buffer :attr:`queue`, then call :meth:`advance` to parse as much as possible.

        If *data* is `None`, then that's the end of the input stream so set :attr:`eof` to True.
        """
        self.feed_without_parsing(data)
        self.advance()
        return self

    def feed_from_file(self, file: ty.IO, buffer_size: int = 65536, finish: bool = True):
        """
        Feed the full contents of *file* as an input. If *finish* is True, then also signal the end of stream.
        """
        while block := file.read(buffer_size):
            self.feed(block)
        if finish:
            self.feed(None)
        return self

    def feed_from_iter(self, iterator, finish: bool = True):
        """
        Feed the contents of *iterator* until it runs out. If *finish* is True, then also signal the end of stream.
        """
        for block in iterator:
            self.feed(block)
        if finish:
            self.feed(None)
        return self

    def advance_one(self) -> bool:
        """
        Return whether any progress was made.

        We consider that progress was made if the generator yielded a truthy value or if the queue became smaller.

        If no progress was made and :attr:`eof` is True and the generator has not yet exited, then raise
        :exc:`UnexpectedEOFError`.
        """
        q = self.queue
        n = len(q)

        try:
            result = next(self.generator)
        except StopIteration:
            result = None
            self.generator_exited = True
            if q and self.trailing_data_raises:
                raise TrailingDataError
        finally:
            consumed = n - len(q)
            self.position += consumed

        progress = bool(result) or consumed > 0
        if not progress and self.eof and not self.generator_exited:
            raise UnexpectedEOFError
        return progress

    def advance(self) -> None:
        """
        Call :meth:`advance_one` to progress the parsing until no more progress can be made.
        """
        while self.advance_one():
            pass


class BinaryParser(Parser[bytes | bytearray | memoryview]):
    """
    Generator-based binary parser.

    Example::

        import struct

        struc = struct.Struct("!BB")
        output = []

        def parse_func(p: BinaryParser):
            header = yield from p.read_bytes(4)
            if header != b"ABCD":
                raise ValueError("invalid header")

            record_count = yield from p.read_int(2, "big", False)
            for i in range(record_count):
                x, y = yield from p.read_struct(struc)
                output.append((x, y))

        parser = BinaryParser(parse_func)

        parser.feed(b"ABCD\x00\x02\x06\x07\x03\x05")
        parser.feed(b"")  # signal end of stream

        print(output)
        # [(6, 7), (3, 5)]
    """

    def _init_queue(self):
        self.queue = BytesQueue()

    def _read_bytes(self, nbytes: int) -> ty.Generator[None, None, bytes | memoryview | bytearray]:
        yield from self.wait(nbytes)
        return self.queue.popleft(nbytes)

    def read_bytes(self, nbytes: int) -> ty.Generator[None, None, bytes]:
        return bytes((yield from self._read_bytes(nbytes)))

    def wait(self, nbytes: int) -> ty.Generator[None, None, None]:
        q = self.queue
        while len(q) < nbytes:
            yield

    def read_int(self, nbytes: int, byteorder: str, signed: bool) -> ty.Generator[None, None, int]:
        yield from self.wait(nbytes)
        with self.queue.popleft_after(nbytes) as b:
            return int.from_bytes(b, byteorder=byteorder, signed=signed)

    def read_struct(self, struct: _struct.Struct) -> ty.Generator[None, None, list]:
        yield from self.wait(nbytes := struct.size)
        with self.queue.popleft_after(nbytes) as b:
            return struct.unpack(b)

    def read_variable_length_int_7bit(
        self, maximum_length: int, byteorder: str, continuation_bit_value: bool, require_canonical: bool
    ):
        with (q := self.queue).temporary_left() as tmp:
            integers = []
            left = maximum_length
            need_more = True
            while need_more:
                yield from self.wait(1)
                b = q.popleft_any_to(tmp)
                for i, c in enumerate(b):
                    integers.append(c & 127)
                    if (c < 128) == continuation_bit_value:
                        tmp.pop_to(len(b) - i - 1, q)
                        need_more = False
                        break
                    left -= 1
                    if left <= 0:
                        raise ValueError("integer too long")

            # Now we assemble it back into one integer.
            if byteorder == "big":
                top = integers[0]
                integers_ = reversed(integers)
            elif byteorder == "little":
                top = integers[-1]
                integers_ = integers
            else:
                raise ValueError('byteorder must be "big" or "little"')

            if require_canonical and top == 0 and len(integers) > 1:
                raise ValueError("non-canonical encoding")

            result = sum(x << (i * 7) for i, x in enumerate(integers_))

            tmp.clear()
            return result
