from __future__ import annotations

import abc
import contextlib
import dataclasses as dc
import io
from collections import deque

import typing as ty

from ._util import repr_helper


class NeedMoreItemsError(IndexError):
    pass


def atomic(function):
    """
    In a future/better version of Python, maybe it will be possible to temporarily
    disable KeyboardInterrupt and other exceptions. This is currently a no-op.
    """
    return function


T = ty.TypeVar("T")


@dc.dataclass(init=False, slots=True, weakref_slot=True)
class SolidQueue(ty.Generic[T], abc.ABC):
    """
    Abstract class implementing a queue using sequences of items.

    This data structure is **not** thread-safe.
    """

    data: deque[T] = dc.field()
    length: int = dc.field()

    def __init__(self, iterable=()):
        self.data = deque()
        self.length = 0
        for x in iterable:
            self.append(x)

    def __len__(self):
        return self.length

    def __bool__(self):
        return bool(self.length)

    def iter_blocks(self):
        return iter(self.data)

    def copy(self):
        return type(self)(self.iter_blocks())

    @property
    def contents(self) -> T:
        """
        Consolidate the sequences of items into one sequence, and then return it.
        """
        return self.peek(self.length)

    @atomic
    def clear(self):
        self.data.clear()
        self.length = 0

    @atomic
    def append(self, array: T) -> None:
        """Add items at the end of the queue."""
        if n := self._len(array):
            self.data.append(array)
            self.length += n

    @atomic
    def appendleft(self, array: T) -> None:
        """
        Place data back at the front of the queue. This effectively undoes the previous :meth:`popleft` operation.
        """
        if n := self._len(array):
            self.data.appendleft(array)
            self.length += n

    def pop(self, n: int) -> T:
        """Remove *n* items from the back of the queue and return them."""
        if not self._consolidate_right(n):
            raise NeedMoreItemsError

        x = self.pop_any()
        assert n == self._len(x)
        return x

    def popleft(self, n: int) -> T:
        """Remove *n* items from the front of the queue and return them."""
        if not self._consolidate_left(n):
            raise NeedMoreItemsError

        x = self.popleft_any()
        assert n == self._len(x)
        return x

    @atomic
    def pop_any(self) -> T | None:
        """Pop a block of items from the back of the queue. Any size may be returned."""
        if not (q := self.data):
            return None
        block = q.pop()
        self.length -= self._len(block)
        return block

    @atomic
    def popleft_any(self) -> T | None:
        """Pop a block of items from the front of the queue. Any size may be returned."""
        if not (q := self.data):
            return None
        block = q.popleft()
        self.length -= self._len(block)
        return block

    @atomic
    def pop_any_to(self, queue: SolidQueue[T]) -> T | None:
        """Transfer a block of items from the back of this queue to the front of another queue."""
        if (x := self.pop_any()) is not None:
            queue.appendleft(x)
        return x

    @atomic
    def popleft_any_to(self, queue: SolidQueue[T]) -> T | None:
        """Transfer a block of items from the front of this queue to the back of another queue."""
        if (x := self.popleft_any()) is not None:
            queue.append(x)
        return x

    def pop_to(self, n: int, queue: SolidQueue[T]) -> None:
        """Transfer *n* items from the back of this queue to the front of another queue."""
        if n > self.length:
            raise NeedMoreItemsError

        while n > 0:
            if self._len(self.data[-1]) > n:
                self.peek(n)  # Split last block.

            n -= len(self.pop_any_to(queue))

    def popleft_to(self, n: int, queue: SolidQueue[T]) -> None:
        """Transfer *n* items from the front of this queue to the back of another queue."""
        if n > self.length:
            raise NeedMoreItemsError

        while n > 0:
            if self._len(self.data[0]) > n:
                self.peekleft(n)  # Split last block.

            n -= len(self.popleft_any_to(queue))

    def pop_all_to(self, queue: SolidQueue[T]) -> T | None:
        """Transfer all items from this queue to the front of another queue."""
        while self.pop_any_to(queue) is not None:
            pass

    def popleft_all_to(self, queue: SolidQueue[T]) -> T | None:
        """Transfer all items from this queue to the back of another queue."""
        while self.popleft_any_to(queue) is not None:
            pass

    def peek(self, n: int) -> T | None:
        """
        Get an array of n items from the back, or None if that is not possible. As a side effect,
        the next :meth:`popleft_any` call will remove exactly n items.
        """
        if self._consolidate_right(n):
            return self.data[-1]
        else:
            return None

    def peek_any(self) -> T | None:
        if u := self.data:
            return u[-1]
        else:
            return None

    def peekleft(self, n: int) -> T | None:
        """
        Get an array of n items from the front, or None if that is not possible. As a side effect,
        the next :meth:`popleft_any` call will remove exactly n items.
        """
        if self._consolidate_left(n):
            return self.data[0]
        else:
            return None

    def peekleft_any(self) -> T | None:
        if u := self.data:
            return u[0]
        else:
            return None

    @contextlib.contextmanager
    def popleft_after(self, n: int | None) -> T:
        """
        Control flow magic, used as::

            with self.popleft_after(num_bytes) as data:
                BODY

        If there are less than *n* data items waiting, then raise :exc:`NeedMoreItemsError`.
        Otherwise return those items the *data* variable and execute the code in *BODY*. If
        *BODY* exits without raising an exception, then remove those items from the data items
        queue.

        If *n* is None, any nonzero number of items may be returned.
        """
        if (data := (self.peekleft_any() if n is None else self.peekleft(n))) is None:
            raise NeedMoreItemsError

        yield data

        # no exception was raised if we got here, so we pop it
        popped = self.popleft_any()
        assert n == self._len(popped)

    @contextlib.contextmanager
    def temporary_left(self) -> ty.Iterator[SolidQueue[T]]:
        """
        Control flow magic, used as::

            q = SolidQueue(...)
            with q.temporary_left() as tmp:
                block1 = q.popleft_to(tmp)
                do_stuff_with(block1)

                block2 = q.popleft_to(tmp)
                do_stuff_with(block2)

        At the end of the "with" block, the contents of `tmp` are transferred to the front of this queue.
        """
        tmp = type(self)()
        try:
            yield tmp
        finally:
            tmp.pop_all_to(self)

    @atomic
    def _consolidate_left(self, n: int) -> bool:
        """
        This function attempts to consolidate exactly *n* items from the queue into a single object.

        Pre-conditions:
            - *n* must be an integer representing the number of items needed for consolidation.

        Post-conditions:
            - Returns True if successful, False otherwise.
            - If there are enough items in the queue, they will be consolidated into a single object
              at the front of the queue with length exactly *n*.
        """
        if self.length < n:
            return False

        data = self.data
        left = n
        to_join = []
        while True:
            e = data.popleft()
            left -= (n_e := self._len(e))

            if left >= 0:
                # we did not grab more than we needed
                to_join.append(e)
                if left > 0:
                    # we are not done, keep looping
                    continue
            else:  # left < 0
                # we grabbed more than we needed, we must split it
                e0, e1 = self._split(e, n_e + left)
                to_join.append(e0)

                # put it back
                data.appendleft(e1)

            data.appendleft(to_join[0] if len(to_join) == 1 else self._join(to_join))
            return True

    @atomic
    def _consolidate_right(self, n: int) -> bool:
        """
        Similar to :meth:`_consolidate_left` but operates on the back of the queue instead of the front.
        """
        if self.length < n:
            return False

        data = self.data
        left = n
        to_join = []
        while True:
            e = data.pop()
            left -= self._len(e)

            if left >= 0:
                # we did not grab more than we needed
                to_join.append(e)
                if left > 0:
                    # we are not done, keep looping
                    continue
            else:  # left < 0
                # we grabbed more than we needed, we must split it
                e0, e1 = self._split(e, -left)
                to_join.append(e1)

                # put it back
                data.append(e0)

            data.append(to_join[0] if len(to_join) == 1 else self._join(reversed(to_join)))
            return True

    @atomic
    def swap(self, queue: SolidQueue[T]) -> None:
        """Swap contents with another queue."""
        a = self
        b = queue
        a.data, a.length, b.data, b.length = b.data, b.length, a.data, a.length

    @abc.abstractmethod
    def _join(self, to_join: ty.Iterable[T]) -> T: ...

    @abc.abstractmethod
    def _split(self, array: T, index: int) -> tuple[T, T]: ...

    @abc.abstractmethod
    def _len(self, array: T) -> int: ...


class BytesQueue(SolidQueue[bytes | memoryview]):
    @staticmethod
    def _join(to_join):
        return b"".join(to_join)

    @staticmethod
    def _split(array, index: int):
        array = memoryview(array)
        return array[:index], array[index:]

    @staticmethod
    def _len(array) -> int:
        return len(array)

    def __bytes__(self):
        return self._join(self.data)


class StringQueue(SolidQueue[str]):
    @staticmethod
    def _join(to_join):
        return "".join(to_join)

    @staticmethod
    def _split(array, index: int):
        # inefficient
        return array[:index], array[index:]

    @staticmethod
    def _len(array) -> int:
        return len(array)

    def __str__(self):
        return self._join(self.data)


@dc.dataclass(init=False, repr=False)
class FileAdapterFromGeneratorBytes(io.RawIOBase):
    """
    Use this to turn a generator that yields bytes into a file-like object.
    """

    _generator: ty.Generator[bytes | bytearray | memoryview | None] = dc.field()
    _buffered: bytes | memoryview = dc.field(default=b"")

    def __init__(self, generator: ty.Generator[bytes | bytearray | memoryview | None]):
        self._generator = generator
        super().__init__()

    def _repr_attribs(self):
        return dict(_generator=self._generator, _buffered_count=self._buffered_count, closed=self.closed)

    def __repr__(self):
        return repr_helper(self, self._repr_attribs())

    @property
    def _buffered_count(self):
        return len(self._buffered)

    def readinto(self, b):
        if not (buf := self._buffered):
            # buffer is empty, we must call the generator to get more data
            if not (buf := next(self._generator, b"")):
                if buf is None:
                    # Generator returned None which means "try again later" if non-blocking.
                    return None
                else:
                    # Generator returned an empty block which means EOF.
                    return 0
            if not isinstance(buf, memoryview):
                buf = memoryview(buf)  # enable efficient slicing
        n = min(len(b), len(buf))
        b[:n] = buf[:n]
        self._buffered = buf[n:]
        return n

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return False

    def close(self):
        self._generator.close()
        self._buffered = b""
        super().close()
