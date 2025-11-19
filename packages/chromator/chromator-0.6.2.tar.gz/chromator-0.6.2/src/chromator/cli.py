import argparse
from typing import TYPE_CHECKING

from based_utils.cli import LogLevel
from based_utils.colors import HSLuv
from yachalk import chalk

from . import log
from .shades import InterpolationParams, generate_shades

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

_log = log.get_logger()


def _colored(color: HSLuv, s: str) -> str:
    return chalk.hex(color.contrasting_shade.hex).bg_hex(color.hex)(s)


def _css_color_comment(color: HSLuv) -> str:
    return _colored(color, f"#{color.hex} --> {color}")


def _shades_as_css_variables(
    c_1: HSLuv, c_2: HSLuv | None, *, params: InterpolationParams, label: str
) -> Iterator[str]:
    yield "/*"
    yield "Based on:"
    if c_2:
        c_dark, c_bright = sorted([c_1, c_2])
        yield f"- Darkest:   {_css_color_comment(c_dark)}"
        yield f"- Brightest: {_css_color_comment(c_bright)}"
    else:
        yield _css_color_comment(c_1)
    yield "*/"

    for color in generate_shades(c_1, c_2, params=params):
        num = int(color.lightness * 100)
        color_var = f"--{label}-{num:02d}: #{color.hex}; /* --> {color} */"
        yield _colored(color, color_var)


def check_integer(v: str, *, conditions: Callable[[int], bool] = None) -> int:
    value = int(v)
    if conditions and not conditions(value):
        raise ValueError(value)
    return value


def check_integer_within_range(
    low: int | None, high: int | None
) -> Callable[[str], int]:
    def is_in_within_range(n: int) -> bool:
        return (low is None or n >= low) and (high is None or n <= high)

    def check(v: str) -> int:
        return check_integer(v, conditions=is_in_within_range)

    return check


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("label", type=str)
    parser.add_argument("-c", "--color1", type=str)
    parser.add_argument("-k", "--color2", type=str, default=None)
    parser.add_argument(
        "-n", "--amount", type=check_integer_within_range(0, None), default=19
    )
    parser.add_argument("-i", "--inclusive", action="store_true", default=False)
    parser.add_argument(
        "-d", "--dynamic-range", type=check_integer_within_range(0, 100), default=0
    )
    args = parser.parse_args()

    with log.context(LogLevel.INFO):
        for line in _shades_as_css_variables(
            HSLuv.from_hex(args.color1),
            HSLuv.from_hex(args.color2),
            params=InterpolationParams(
                args.amount, args.inclusive, args.dynamic_range / 100
            ),
            label=args.label,
        ):
            _log.info(line)
