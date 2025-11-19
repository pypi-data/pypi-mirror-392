import argparse
from typing import TYPE_CHECKING

from based_utils.cli import LogLevel
from based_utils.colors import HSLuv
from yachalk import chalk

from . import log
from .shades import InterpolationParams, generate_shades

if TYPE_CHECKING:
    from collections.abc import Iterator

_log = log.get_logger()


def _colored(color: HSLuv, s: str = None) -> str:
    bg_hex = color.hex
    fg_hex = color.contrasting_shade.hex
    return chalk.hex(fg_hex).bg_hex(bg_hex)(s or bg_hex)


def _css_color_comment(color: HSLuv) -> str:
    return f"""
{_colored(color)}:
- Hue: {color.hue:.1f}°
- Saturation: {color.saturation:.1f}%
- Lightness: {color.lightness:.1f}%"""


def _shades_as_css_variables(
    c_1: HSLuv, c_2: HSLuv | None, *, params: InterpolationParams, label: str
) -> Iterator[str]:
    yield "/*"
    yield "Based on:"
    yield _css_color_comment(c_1)
    if c_2:
        yield _css_color_comment(c_2)
    yield "*/"

    for color in generate_shades(c_1, c_2, params=params):
        color_var = f"--{label}-{int(color.lightness):02d}: #{color.hex};"
        yield _colored(color, color_var)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("label", type=str)
    parser.add_argument("-c", "--color1", type=str)
    parser.add_argument("-k", "--color2", type=str, default=None)
    parser.add_argument(
        "-s", "--step", type=int, default=5, choices=[1, 2, 4, 5, 10, 20, 25, 50]
    )
    parser.add_argument("-i", "--inclusive", action="store_true", default=False)
    parser.add_argument(
        "-d", "--dynamic-range", type=int, default=0, choices=list(range(101))
    )
    args = parser.parse_args()

    with log.context(LogLevel.INFO):
        for line in _shades_as_css_variables(
            HSLuv.from_hex(args.color1),
            HSLuv.from_hex(args.color2),
            params=InterpolationParams(
                args.step, args.inclusive, args.dynamic_range / 100
            ),
            label=args.label,
        ):
            _log.info(line)
