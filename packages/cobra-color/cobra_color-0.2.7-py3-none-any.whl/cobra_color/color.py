# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from typing import (Any, List, Tuple, Optional, Iterable, Union)

from .types import (ColorName, StyleName)


# code of colors
_COLOR_CODE = {
    "d": "0",  # dark/black
    "r": "1",  # red
    "g": "2",  # green
    "y": "3",  # yellow
    "b": "4",  # blue
    "m": "5",  # magenta
    "c": "6",  # cyan
    "w": "7",  # white
}
# code of styles
_STYLE_CODE = {
    "bold": "1",
    "dim": "2",
    "italic": "3",
    "udl": "4",
    "underline": "4",
    "blink": "5",
    "selected": "7",
    "disappear": "8",
    "del": "9",
    "delete": "9"
}


def ctext(
    text: Any,
    fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    styles: Optional[Iterable[StyleName]] = None
) -> ColorStr:
    r"""
    Generate a colored string for terminal output.

    Parameters
    ----------
        text : Any
            The text content to be colored.

        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the string.
            - _ColorName_: `Basic 8 color` OR `Light 8 color`, compatible with older terminals;

            NOTE: _ColorName_: `d`(black); `r`(red); `g`(green); `y`(yellow); `b`(blue); `m`(magenta); `c`(cyan); `w`(white). Prefix `l` means Light 8 color.

            - _int_: `256 color`, compatible with most terminals;

            NOTE: `0-7`: Basic 8 color; `8-15`: Light 8 color; `16-231`: 6x6x6 color cube; `232-255`: grayscale from dark to light.

            - _Iterable[int]_: `True color`, compatible with modern terminals.

            NOTE: Each value should be in range `0-255`, representing `R`, `G`, `B` respectively.

            - `None`: No color applied.

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the string.
            (Same format and rules as `fg`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the string.

            NOTE: _StyleName_: `bold`, `dim`, `italic`, `udl`, `underline`, `blink`, `selected`, `disappear`, `del`, `delete`.

    Returns
    -------
        ColorStr
            The colored string with ANSI escape codes. Usage same as `str`, with `plain`, `color_only`, `style_only` properties. You can combine multiple colored strings using `+` operator or `+=` operator.
    """
    return ColorStr.from_str(text, fg=fg, bg=bg, styles=styles)


def compile_template(
    fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    styles: Optional[Iterable[StyleName]] = None
):
    r"""
    Create a template for generating colored strings with preset styles.

    Parameters
    ----------
        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the string.
            (Same format and rules as in `ctext`.)

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the string.
            (Same format and rules as in `ctext`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the string.
            (Same format and rules as in `ctext`.)

    Returns
    -------
        Template
            A template object that can be used to generate colored strings with the preset styles.
    """
    return Template(fg=fg, bg=bg, styles=styles)


class Template():
    r"""
    A template class for generating colored strings with preset styles.

    Parameters
    ----------
        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the string.
            (Same format and rules as in `ctext`.)

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the string.
            (Same format and rules as in `ctext`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the string.
            (Same format and rules as in `ctext`.)
    """
    def __init__(
        self,
        fg: Any = None,
        bg: Any = None,
        styles: Any = None,
    ):
        self.__fg = fg
        self.__bg = bg
        self.__styles = styles

    def format(self, text: Any) -> ColorStr:
        r"""
        Generate a colored string using the preset template.

        Parameters
        ----------
            text : Any
                The text content to be colored.

        Returns
        -------
            ColorStr
                The colored string with ANSI escape codes. Usage same as `str`, with `plain`, `color_only`, `style_only` properties.
        """
        return ColorStr.from_str(text, fg=self.__fg, bg=self.__bg, styles=self.__styles)

    def __call__(self, text: Any) -> ColorStr:
        r"""
        Generate a colored string using the preset template.
        """
        return self.format(text)


class ColorStr(str):
    r"""
    A string class that supports ANSI color and style formatting while preserving plain text.

    NOTE: Usage same as `str`, with `plain`, `color_only`, `style_only` properties.
    """
    __slots__ = ("_SEGMENTS",)
    _SEGMENTS: List[Tuple[str, str, str]]  # list of (plain, color_codes, style_codes)

    @classmethod
    def from_str(
        cls,
        _str: Any,
        fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        styles: Optional[Iterable[StyleName]] = None
    ):
        r"""
        Create a ColorStr from a regular string with specified color and style.
        """
        plain = str(_str)
        if plain and (fg is not None or bg is not None or styles is not None):
            style_code, color_code = _get_ansi_code(
                fg=fg,
                bg=bg,
                styles=styles if styles is not None else []
            )
        else:
            style_code = ""
            color_code = ""
        segments = [(plain, color_code, style_code)]

        obj = super().__new__(cls, _assemble_segments(segments))
        obj._SEGMENTS = segments

        return obj

    def __new__(
        cls,
        *segments: Tuple[str, str, str]
    ):
        assert all(isinstance(seg, Tuple) and len(seg) == 3 for seg in segments), "Each Segment Must Be A Tuple Of (plain, color_code, style_code)."
        obj = super().__new__(cls, _assemble_segments(segments))
        obj._SEGMENTS = list(segments)

        return obj

    def __add__(self, other_str: str):
        other_c_str = other_str if isinstance(other_str, ColorStr) else ColorStr.from_str(other_str)
        return ColorStr(*(self._SEGMENTS + other_c_str._SEGMENTS))

    def __iadd__(self, other_str: str):
        other_c_str = other_str if isinstance(other_str, ColorStr) else ColorStr.from_str(other_str)
        self._SEGMENTS.extend(other_c_str._SEGMENTS)
        return ColorStr(*(self._SEGMENTS))

    @property
    def plain(self) -> str:
        r"""
        The plain text without ANSI formatting.
        """
        return _assemble_segments(self._SEGMENTS, use_color=False, use_style=False)

    @property
    def color_only(self) -> str:
        r"""
        The colored text without styles.
        """
        return _assemble_segments(self._SEGMENTS, use_color=True, use_style=False)

    @property
    def style_only(self) -> str:
        r"""
        The styled text without colors.
        """
        return _assemble_segments(self._SEGMENTS, use_color=False, use_style=True)


def _get_ansi_code(
    fg: Optional[Union[ColorName, int, Iterable[int]]],
    bg: Optional[Union[ColorName, int, Iterable[int]]],
    styles: Iterable[StyleName]
) -> Tuple[str, str]:
    r"""
    Generate ANSI code for style and color.
    """
    def _parse_color(
        c: Union[ColorName, int, Iterable[int]],
        is_fg: bool
    ) -> str:
        r"""
        Parse the color input into ANSI color code.
        """
        parse = ""
        if isinstance(c, str):
            # Basic 8 color OR Light 8 color
            if c in _COLOR_CODE:
                # Basic 8 color
                parse = ("3" if is_fg else "4") + _COLOR_CODE[c]
            elif c.startswith("l") and len(c) == 2 and c[1] in _COLOR_CODE:
                # Light 8 color
                parse = ("9" if is_fg else "10") + _COLOR_CODE[c[1]]
        elif isinstance(c, int) and 0 <= c <= 255:
            # 256 color
            parse = ("38" if is_fg else "48") + f";5;{c}"
        elif isinstance(c, Iterable) and all(isinstance(val, int) and 0 <= val <= 255 for val in c):
            # True color
            rgb = (list(c) + [0, 0, 0])[:3]
            parse = ("38" if is_fg else "48") + f";2;{rgb[0]};{rgb[1]};{rgb[2]}"

        return parse

    # style_code
    if isinstance(styles, Iterable):
        style_code = ";".join(_STYLE_CODE[s] for s in styles if s in _STYLE_CODE)
    else:
        style_code = ""
    # color_code
    foreground = "" if fg is None else _parse_color(fg, is_fg=True)
    background = "" if bg is None else _parse_color(bg, is_fg=False)
    color_code = ";".join((foreground, background)).strip(";")

    return style_code, color_code


def _assemble_segments(
    segments: Iterable[Tuple[str, str, str]],
    use_color: bool = True,
    use_style: bool = True
) -> str:
    r"""
    Assemble segments into a single ANSI formatted string.
    """
    result = ""
    for plain, color_code, style_code in segments:
        if not plain:
            continue

        if use_color and use_style:
            codes = f"{style_code};{color_code}"
        elif use_color or use_style:
            codes = color_code if use_color else style_code
        else:
            codes = ""
        codes = codes.strip(";")
        if codes:
            result += f"\033[{codes}m{plain}\033[0m"
        else:
            result += plain

    return result
