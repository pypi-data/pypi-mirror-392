# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from typing import (Any, Tuple, Optional, Iterable, Union)

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
    "blink": "5",
    "selected": "7",
    "disappear": "8",
    "del": "9"
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

            NOTE: _StyleName_: `bold`, `dim`, `italic`, `udl`, `blink`, `selected`, `disappear`, `del`.

    Returns
    -------
        ColorStr
            The colored string with ANSI escape codes. Usage same as `str`, with `plain`, `color_only`, `style_only` properties.
    """
    return ColorStr(text, fg=fg, bg=bg, styles=styles)


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
        **kwargs: Any
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
        return ctext(
            text,
            fg=self.__fg,
            bg=self.__bg,
            styles=self.__styles
        )

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
    _PLAIN: str
    _STYLE_CODES: str
    _COLOR_CODES: str

    def __new__(
        cls,
        text: Any,
        fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        styles: Optional[Iterable[StyleName]] = None
    ):
        plain_text = str(text)
        if plain_text and (fg is not None or bg is not None or styles is not None):
            style_codes, color_codes = ColorStr._get_ansi_codes(
                fg=fg,
                bg=bg,
                styles=styles if styles is not None else []
            )
            _codes = ";".join((style_codes, color_codes)).strip(";")
            ansi_text = f"\033[{_codes}m{plain_text}\033[0m"
        else:
            style_codes = ""
            color_codes = ""
            ansi_text = plain_text

        obj = super().__new__(cls, ansi_text)

        setattr(obj, "_PLAIN", plain_text)
        setattr(obj, "_STYLE_CODES", style_codes)
        setattr(obj, "_COLOR_CODES", color_codes)

        return obj

    @staticmethod
    def _parse_color(
        c: Union[ColorName, int, Iterable[int]],
        is_fg: bool
    ) -> str:
        r"""
        Parse the color input into ANSI color codes.
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

    @staticmethod
    def _get_ansi_codes(
        fg: Optional[Union[ColorName, int, Iterable[int]]],
        bg: Optional[Union[ColorName, int, Iterable[int]]],
        styles: Iterable[StyleName]
    ) -> Tuple[str, str]:
        r"""
        Generate ANSI codes for styles and colors.
        """
        # style_codes
        if isinstance(styles, Iterable):
            style_codes = ";".join(_STYLE_CODE[s] for s in styles if s in _STYLE_CODE)
        else:
            style_codes = ""
        # color_codes
        foreground = "" if fg is None else ColorStr._parse_color(fg, is_fg=True)
        background = "" if bg is None else ColorStr._parse_color(bg, is_fg=False)
        color_codes = ";".join((foreground, background)).strip(";")

        return style_codes, color_codes

    @property
    def plain(self) -> str:
        r"""
        The plain text without ANSI formatting.
        """
        return self._PLAIN

    @property
    def color_only(self) -> str:
        r"""
        The colored text without styles.
        """
        if not self._COLOR_CODES:
            return self._PLAIN
        return f"\033[{self._COLOR_CODES}m{self._PLAIN}\033[0m"

    @property
    def style_only(self) -> str:
        r"""
        The styled text without colors.
        """
        if not self._STYLE_CODES:
            return self._PLAIN
        return f"\033[{self._STYLE_CODES}m{self._PLAIN}\033[0m"
