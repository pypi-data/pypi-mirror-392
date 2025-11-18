from __future__ import annotations

import struct
import zlib
from collections import Counter
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Final, Iterator, Mapping, overload

from ._color import PAT_TO_COLOR, Color


if TYPE_CHECKING:
    from typing_extensions import Self

WIDTH = 240
"""Screen width in pixels.

This is the default width of Frame returned by Firefly.get_frame.
"""

HEIGHT = 160
"""Screen height in pixels.

This is the default height of Frame returned by Firefly.get_frame.
"""


_COLOR_TO_PAT: Final[Mapping[int, str]] = {
    v: k for k, v in PAT_TO_COLOR.items() if k.isascii() or k in '◔◑◕'
}
_BYTE_ORDER: Final = 'little'

RED = '\033[31m'
GREEN = '\033[32m'
END = '\033[0m'


class Frame:
    __slots__ = ('_buf', '_width')
    _buf: list[Color]
    _width: int

    def __init__(self, colors: list[Color], *, width: int) -> None:
        assert type(colors[0]) is Color
        assert 0 <= width <= WIDTH
        assert 0 < len(colors) <= WIDTH * HEIGHT
        assert len(colors) % width == 0
        self._width = width
        self._buf = colors

    @classmethod
    def _from_rgb16(cls, buf: list[int], *, width: int) -> Self:
        assert type(buf[0]) is int
        colors = [Color._from_rgb16(c) for c in buf]
        return cls(colors, width=width)

    @classmethod
    def from_rgb24(cls, buf: list[int], *, width: int) -> Self:
        assert type(buf[0]) is int
        colors = [Color.from_rgb24(c) for c in buf]
        return cls(colors, width=width)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return len(self._buf) // self._width

    def at(self, x: int, y: int | None = None) -> Color:
        """Get the color of the pixel with the given coordinates.

        Can accept either x and y or a flat single number index of the pixel
        in the frame buffer array.
        """
        if y is not None:
            assert 0 <= x < self.width
            assert 0 <= y < self.height
            x = y * self._width + x
        return self._buf[x]

    def get_sub(
        self, *,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
    ) -> Self:
        """Get a subregion of the frame.

        The region must be fully within the frame.
        """
        if width is None:
            width = self.width - x
        if height is None:
            height = self.height - y
        assert 0 <= x < self.width
        assert 0 <= y < self.height
        assert 0 <= width < self.width
        assert 0 <= height < self.height
        assert 0 <= x + width <= self.width
        assert 0 <= y + height <= self.height

        res_buf = []
        for line_no in range(y, y + height):
            start = line_no * self._width + x
            end = start + width
            line = self._buf[start:end]
            res_buf.extend(line)
        return type(self)(res_buf, width=width)

    def to_dict(self) -> dict[Color, int]:
        """Get the dict of how many pixels of each color the frame has.

        The dict contains only colors present on the screen.
        """
        return dict(self.to_counter())

    def to_set(self) -> set[Color]:
        """Get the set of all colors present on the frame.
        """
        return set(self.to_counter())

    def to_counter(self) -> Counter[Color]:
        """Get the count of pixels of each color on the frame.
        """
        return Counter(self)

    def assert_match(self, expected: str | Path | BinaryIO | Frame) -> None:
        """Assert that the frame matches a pattern, a Frame, or a snapshot.

        Raises AssertionError on mismatch. The error message contains a nice diff
        and some helpful information about the failure.
        """
        if isinstance(expected, str):
            self._match_pattern(expected)
            return
        if isinstance(expected, Frame):
            self._match_frame(expected)
            return
        if isinstance(expected, Path) and not expected.is_file():
            expected.parent.mkdir(exist_ok=True)
            self.write(expected)
            return
        self._match_snapshot(expected)

    def _match_pattern(self, pattern: str) -> None:
        """Raise AssertionError if the Frame doesn't match the given pattern.
        """
        report = []
        patterns = [p.strip() for p in pattern.splitlines()]
        patterns = [p for p in patterns if p]
        failures = 0
        for i, pattern_line in enumerate(patterns):
            pattern_line = pattern_line.strip()
            if self._check_line(i, pattern_line):
                color = GREEN
                sign = '=='
            else:
                color = RED
                sign = '!='
                failures += 1
            actual = self._format_line(i)[:len(pattern_line)]
            report.append(f'{color}{actual} {sign} {pattern_line}{END}')
        if failures:
            msg = '🙅 Frame does not match the pattern.\n'
            msg += f'Lines differ: {failures}.\n'
            msg += 'Diff:\n'
            msg += '\n'.join(report)
            raise AssertionError(msg)

    def _match_snapshot(self, source: BinaryIO | Path) -> None:
        """Raise AssertionError if the Frame doesn't match the given snapshot.
        """
        expected = self.read(source)
        path = source if isinstance(source, Path) else None
        self._match_frame(expected, path)

    def _match_frame(self, expected: Self, path: Path | None = None) -> None:
        """Raise AssertionError if the Frame doesn't match the given Frame.
        """
        if self.width != expected.width:
            msg = '👉 Unexpected Frame.width. '
            msg += f'Actual: {self.width}. Expected: {expected.width}.'
            raise AssertionError(msg)
        if self.height != expected.height:
            msg = '👆 Unexpected Frame.height. '
            msg += f'Actual: {self.height}. Expected: {expected.height}.'
            raise AssertionError(msg)

        if self._buf == expected._buf:
            return

        msg = '🖼 Unexpected Frame content.\n'
        if path is not None:
            msg += f'Snapshot: {path}.\n'
        bad_pixels = sum(a != e for a, e in zip(self._buf, expected._buf))
        msg += f'Pixels mismatch: {bad_pixels} out of {len(self._buf)}.\n'
        bad_lines = 0
        first_bad = None
        last_bad = 0
        width = self._width
        for i in range(0, len(self._buf), width):
            act_line = self._buf[i:i+width]
            exp_line = expected._buf[i:i+width]
            if act_line != exp_line:
                line_no = i // width
                last_bad = line_no
                if first_bad is None:
                    first_bad = line_no
                bad_lines += 1
        msg += f'Lines mismatch: {bad_lines} out of {self.height}.\n'
        msg += f'First mismatched line: {first_bad} (0-indexed).\n'
        msg += f'Last mismatched line: {last_bad} (0-indexed).\n'
        raise AssertionError(msg)

    @classmethod
    def read(cls, stream: BinaryIO | Path) -> Self:
        """Read from a file a Frame serialized with Frame.write.
        """
        if isinstance(stream, Path):
            with stream.open('rb') as bin_stream:
                return cls.read(bin_stream)
        decomp_bytes = zlib.decompress(stream.read())
        decomp_stream = BytesIO(decomp_bytes)
        width = int.from_bytes(decomp_stream.read(2), _BYTE_ORDER)
        buf = []
        while True:
            chunk = decomp_stream.read(2)
            if len(chunk) != 2:
                break
            buf.append(int.from_bytes(chunk, _BYTE_ORDER))
        return cls._from_rgb16(buf, width=width)

    def write(self, stream: BinaryIO | Path) -> None:
        """Serialize the Frame into a file as a binary.
        """
        if isinstance(stream, Path):
            with stream.open('wb') as bin_stream:
                self.write(bin_stream)
                return
        bs = bytearray()
        bs.extend(self._width.to_bytes(2, _BYTE_ORDER))
        for pixel in self._buf:
            bs.extend(pixel._rgb16.to_bytes(2, _BYTE_ORDER))
        stream.write(zlib.compress(bs))

    def to_png(self, stream: BinaryIO | Path) -> None:
        """Save the Frame as a PNG file.
        """
        if isinstance(stream, Path):
            with stream.open('wb') as bin_stream:
                self.to_png(bin_stream)
                return
        # https://gitlab.com/drj11/minpng/-/blob/main/minpng.py?ref_type=heads
        stream.write(bytearray([137, 80, 78, 71, 13, 10, 26, 10]))
        header = struct.pack(
            '>2LBBBBB',
            self.width,
            self.height,
            8, 2, 0, 0, 0,
        )
        _write_chunk(stream, b'IHDR', header)
        bs = bytearray()
        for i in range(0, len(self._buf), self._width):
            bs.append(0)
            for pixel in self._buf[i:i+self._width]:
                rgb24 = (pixel.r << 16) | (pixel.g << 8) | pixel.b
                bs.extend(rgb24.to_bytes(3, 'big'))
        _write_chunk(stream, b'IDAT', zlib.compress(bs))
        _write_chunk(stream, b'IEND', bytes())

    def __iter__(self) -> Iterator[Color]:
        """Iterate over all pixels in the frame.

        Iteration goes left-to-right and top-to-bottom,
        like scanlines in the old CRT displays or how you read English text.
        """
        return iter(self._buf)

    def __contains__(self, val: object) -> bool:
        """Check if the Frame contains a pixel of the given Color.
        """
        if isinstance(val, int):
            assert 0x000000 <= val <= 0xFFFFFF
            return Color.from_rgb24(val) in self._buf
        if isinstance(val, Color):
            return val in self._buf
        t = type(val).__name__
        raise TypeError(f'Frame can contain only Color, not {t}')

    @overload
    def __getitem__(self, i: int | tuple[int, int]) -> Color:
        pass

    # https://github.com/python/typeshed/issues/8647
    @overload
    def __getitem__(self, i: slice) -> Self:
        pass

    def __getitem__(self, i: int | tuple[int, int] | slice) -> Color | Self:
        if isinstance(i, tuple):
            x, y = i
            if x >= self._width:
                raise IndexError('x is out of range')
            i = y * self._width + x
        if isinstance(i, slice):
            assert i.step is None
            x, y = i.start
            ex, ey = i.stop
            return self.get_sub(x=x, y=y, width=ex - x, height=ey - y)
        return self._buf[i]

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            patterns = [p.strip() for p in other.splitlines()]
            patterns = [p for p in patterns if p]
            for i, pattern in enumerate(patterns):
                if not self._check_line(i, pattern):
                    return False
            return True
        if isinstance(other, type(self)):
            if self._width != other._width:
                raise TypeError('can only compare frames of the same width')
            return self._buf == other._buf
        return NotImplemented

    def __str__(self) -> str:
        """Represent the frame as a pattern.
        """
        res = ''
        for i in range(self._width):
            res += self._format_line(i) + '\n'
        return res

    def __len__(self) -> int:
        return len(self._buf)

    def _format_line(self, line_no: int) -> str:
        """Represent the given line as a pattern.
        """
        i = line_no * self._width
        raw_line = self._buf[i:i+self._width]
        return ''.join(_COLOR_TO_PAT.get(c._rgb16, '*') for c in raw_line)

    def _check_line(self, i: int, pattern: str) -> bool:
        """Check if the given line matches the given pattern.

        The pattern can be shorter than the line.
        In that case, only the line prefix is checked.
        """
        pattern = ''.join(pattern.split())  # remove spaces
        assert 0 < len(pattern) <= self._width
        start = i * self._width
        end = start + self._width
        line = self._buf[start:end]
        return all(act == exp for act, exp in zip(line, pattern))


def _write_chunk(out: BinaryIO, chunk_type: bytes, data: bytes) -> None:
    """Write a PNG chunk.

    https://en.wikipedia.org/wiki/PNG
    """
    assert len(chunk_type) == 4
    out.write(struct.pack('>L', len(data)))
    out.write(chunk_type)
    out.write(data)
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(data, checksum)
    out.write(struct.pack('>L', checksum))
