from __future__ import annotations

from colorsys import rgb_to_hls, rgb_to_hsv, rgb_to_yiq
from dataclasses import dataclass
from typing import ClassVar, Final, Mapping

from . import _rust


@dataclass(frozen=True)
class RGB24:
    r: int
    g: int
    b: int

    def __int__(self) -> int:
        return (self.r << 16) | (self.g << 8) | self.b


class Color:
    """An RGB color of a pixel on the Frame.
    """
    __slots__ = ('_raw',)
    _raw: _rust.Color

    # Colors from the default color palette (SWEETIE 16)
    # https://lospec.com/palette-list/sweetie-16
    #
    # It could be an enum but enums work better when there is a well-known
    # in advance list of possible values.

    BLACK: ClassVar[Color]
    """The black color from the default palette (SWEETIE-16): #1A1C2C.
    """

    PURPLE: ClassVar[Color]
    """The purple color from the default palette (SWEETIE-16): #5D275D.
    """

    RED: ClassVar[Color]
    """The red color from the default palette (SWEETIE-16): #B13E53.
    """

    ORANGE: ClassVar[Color]
    """The orange color from the default palette (SWEETIE-16): #EF7D57.
    """

    YELLOW: ClassVar[Color]
    """The yellow color from the default palette (SWEETIE-16): #FFCD75.
    """

    LIGHT_GREEN: ClassVar[Color]
    """The light green color from the default palette (SWEETIE-16): #A7F070.
    """

    GREEN: ClassVar[Color]
    """The green color from the default palette (SWEETIE-16): #38B764.
    """

    DARK_GREEN: ClassVar[Color]
    """The dark green color from the default palette (SWEETIE-16): #257179.
    """

    DARK_BLUE: ClassVar[Color]
    """The dark blue color from the default palette (SWEETIE-16): #29366F.
    """

    BLUE: ClassVar[Color]
    """The blue color from the default palette (SWEETIE-16): #3B5DC9.
    """

    LIGHT_BLUE: ClassVar[Color]
    """The light blue color from the default palette (SWEETIE-16): #41A6F6.
    """

    CYAN: ClassVar[Color]
    """The cyan color from the default palette (SWEETIE-16): #73EFF7.
    """

    WHITE: ClassVar[Color]
    """The white color from the default palette (SWEETIE-16): #F4F4F4.
    """

    LIGHT_GRAY: ClassVar[Color]
    """The light gray color from the default palette (SWEETIE-16): #94B0C2.
    """

    GRAY: ClassVar[Color]
    """The gray color from the default palette (SWEETIE-16): #566C86.
    """

    DARK_GRAY: ClassVar[Color]
    """The dark gray color from the default palette (SWEETIE-16): #333C57.
    """

    # Extreme colors. Useful for debugging.

    TRUE_BLACK: ClassVar[Color]
    """Purely black color: #000000.
    """

    TRUE_WHITE: ClassVar[Color]
    """Purely white color: #FFFFFF.
    """

    TRUE_RED: ClassVar[Color]
    """Purely red color: #FF0000.
    """

    TRUE_GREEN: ClassVar[Color]
    """Purely green color: #00FF00.
    """

    TRUE_BLUE: ClassVar[Color]
    """Purely blue color: #0000FF.
    """

    @classmethod
    def from_rgb24(cls, raw: int) -> Color:
        """Create a new color from a true-color RGB representation.

        For example, 0x00FF00 represents pure green.

        Keep in mind that internally the color in Firefly is represented as
        16 bits, not 24, so some precision is lost in conversions.
        """
        self = cls()
        r = (raw >> 16) & 0xFF
        g = (raw >> 8) & 0xFF
        b = raw & 0xFF
        self._raw = _rust.Color(r, g, b)
        return self

    @classmethod
    def _from_rgb16(cls, raw: int) -> Color:
        self = cls()
        self._raw = _rust.Color.from_rgb16(raw)
        return self

    @property
    def _rgb24(self) -> RGB24:
        r, g, b = self._raw.to_rgb()
        return RGB24(r, g, b)

    @property
    def _rgb16(self) -> int:
        return self._raw.to_rgb16()

    @property
    def r(self) -> int:
        """The red component of the RGB color representation.

        A value from from 0 (no red) to 255 (as red as it gets).
        """
        return self._rgb24.r

    @property
    def g(self) -> int:
        """The green component of the RGB color representation.

        A value from from 0 (no green) to 255 (as green as it gets).
        """
        return self._rgb24.g

    @property
    def b(self) -> int:
        """The blue component of the RGB color representation.

        A value from from 0 (no blue) to 255 (as blue as it gets).
        """
        return self._rgb24.b

    @property
    def rgb(self) -> tuple[float, float, float]:
        """Color RGB representation: Reg, Green, and Blue.

        Each value is in the [0.0..1.0] range.

        https://en.wikipedia.org/wiki/RGB_color_model
        """
        rgb = self._rgb24
        return (rgb.r / 255, rgb.g / 255, rgb.b / 255)

    @property
    def hls(self) -> tuple[float, float, float]:
        """Color HLS representation: Hue, Lightness, and Saturation.

        Each value is in the [0.0..1.0] range.

        https://en.wikipedia.org/wiki/HSL_and_HSV
        """
        rgb = self._rgb24
        return rgb_to_hls(rgb.r / 255, rgb.g / 255, rgb.b / 255)

    @property
    def hsv(self) -> tuple[float, float, float]:
        """Color HSV representation: Hue, Saturation, and Value (Brightness).

        Each value is in the [0.0..1.0] range.

        https://en.wikipedia.org/wiki/HSL_and_HSV
        """
        rgb = self._rgb24
        return rgb_to_hsv(rgb.r / 255, rgb.g / 255, rgb.b / 255)

    @property
    def yiq(self) -> tuple[float, float, float]:
        """Color YIQ representation.

        https://en.wikipedia.org/wiki/YIQ
        """
        rgb = self._rgb24
        return rgb_to_yiq(rgb.r / 255, rgb.g / 255, rgb.b / 255)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            if other == '.':
                return True
            color = PAT_TO_COLOR[other]
            return self._rgb16 == color
        if isinstance(other, Color):
            return self._rgb16 == other._rgb16
        if isinstance(other, int):
            assert 0x000000 <= other <= 0xFFFFFF
            return self._rgb16 == Color.from_rgb24(other)._rgb16
        return NotImplemented

    def __repr__(self) -> str:
        try:
            return _COLOR_TO_REPR[self._rgb16]
        except AttributeError:  # pragma: no cover
            # Partially initialized class, no value is set yet.
            # Might be reached if there is a failure in Color.__init__
            # and pytest includes repr in the error report.
            return f'{type(self).__name__}(???)'
        except KeyError:
            return f'{type(self).__name__}.from_rgb24(0x{int(self):06X})'

    def __str__(self) -> str:
        return f'#{int(self):06X}'

    def __int__(self) -> int:
        return int(self._rgb24)

    def __hash__(self) -> int:
        return hash(self._rgb16)


# Color instances can be initialized only after Color class is created.
Color.BLACK = Color.from_rgb24(0x1A1C2C)
Color.PURPLE = Color.from_rgb24(0x5D275D)
Color.RED = Color.from_rgb24(0xB13E53)
Color.ORANGE = Color.from_rgb24(0xEF7D57)
Color.YELLOW = Color.from_rgb24(0xFFCD75)
Color.LIGHT_GREEN = Color.from_rgb24(0xA7F070)
Color.GREEN = Color.from_rgb24(0x38B764)
Color.DARK_GREEN = Color.from_rgb24(0x257179)
Color.DARK_BLUE = Color.from_rgb24(0x29366F)
Color.BLUE = Color.from_rgb24(0x3B5DC9)
Color.LIGHT_BLUE = Color.from_rgb24(0x41A6F6)
Color.CYAN = Color.from_rgb24(0x73EFF7)
Color.WHITE = Color.from_rgb24(0xF4F4F4)
Color.LIGHT_GRAY = Color.from_rgb24(0x94B0C2)
Color.GRAY = Color.from_rgb24(0x566C86)
Color.DARK_GRAY = Color.from_rgb24(0x333C57)

Color.TRUE_BLACK = Color.from_rgb24(0x000000)
Color.TRUE_WHITE = Color.from_rgb24(0xFFFFFF)
Color.TRUE_RED = Color.from_rgb24(0xFF0000)
Color.TRUE_GREEN = Color.from_rgb24(0x00FF00)
Color.TRUE_BLUE = Color.from_rgb24(0x0000FF)

PAT_TO_COLOR: Final[Mapping[str, int]] = {
    'K': Color.BLACK._rgb16,
    'P': Color.PURPLE._rgb16,
    'R': Color.RED._rgb16,
    'O': Color.ORANGE._rgb16,
    'Y': Color.YELLOW._rgb16,
    'g': Color.LIGHT_GREEN._rgb16,
    'G': Color.GREEN._rgb16,
    'D': Color.DARK_GREEN._rgb16,
    'd': Color.DARK_BLUE._rgb16,
    'B': Color.BLUE._rgb16,
    'b': Color.LIGHT_BLUE._rgb16,
    'C': Color.CYAN._rgb16,
    'W': Color.WHITE._rgb16,
    '◔': Color.LIGHT_GRAY._rgb16,
    '◑': Color.GRAY._rgb16,
    '◕': Color.DARK_GRAY._rgb16,

    # For completeness with gray representations.
    # Experimental. In dark theme, white looks black and black looks white.
    '○': Color.WHITE._rgb16,
    '●': Color.BLACK._rgb16,

    # Experimental. Emojis show actual colors but they are also interpreted
    # by many terminals as 2 characters which makes the diff misaligned.
    '🖤': Color.BLACK._rgb16,     # ◾
    '💜': Color.PURPLE._rgb16,    # 🟪
    '♥️': Color.RED._rgb16,       # 🟥
    '🧡': Color.ORANGE._rgb16,    # 🟧
    '💛': Color.YELLOW._rgb16,    # 🟨
    '💚': Color.GREEN._rgb16,     # 🟩
    '💙': Color.BLUE._rgb16,      # 🟦
    '🤍': Color.WHITE._rgb16,     # ◽
    '🩶': Color.GRAY._rgb16,
}

_COLOR_TO_REPR: Final[Mapping[int, str]] = {
    Color.BLACK._rgb16: 'Color.BLACK',
    Color.PURPLE._rgb16: 'Color.PURPLE',
    Color.RED._rgb16: 'Color.RED',
    Color.ORANGE._rgb16: 'Color.ORANGE',
    Color.YELLOW._rgb16: 'Color.YELLOW',
    Color.LIGHT_GREEN._rgb16: 'Color.LIGHT_GREEN',
    Color.GREEN._rgb16: 'Color.GREEN',
    Color.DARK_GREEN._rgb16: 'Color.DARK_GREEN',
    Color.DARK_BLUE._rgb16: 'Color.DARK_BLUE',
    Color.BLUE._rgb16: 'Color.BLUE',
    Color.LIGHT_BLUE._rgb16: 'Color.LIGHT_BLUE',
    Color.CYAN._rgb16: 'Color.CYAN',
    Color.WHITE._rgb16: 'Color.WHITE',
    Color.LIGHT_GRAY._rgb16: 'Color.LIGHT_GRAY',
    Color.GRAY._rgb16: 'Color.GRAY',
    Color.DARK_GRAY._rgb16: 'Color.DARK_GRAY',
    Color.TRUE_BLACK._rgb16: 'Color.TRUE_BLACK',
    Color.TRUE_WHITE._rgb16: 'Color.TRUE_WHITE',
    Color.TRUE_RED._rgb16: 'Color.TRUE_RED',
    Color.TRUE_GREEN._rgb16: 'Color.TRUE_GREEN',
    Color.TRUE_BLUE._rgb16: 'Color.TRUE_BLUE',
}
