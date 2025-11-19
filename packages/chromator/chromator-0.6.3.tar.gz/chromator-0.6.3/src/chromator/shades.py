from dataclasses import dataclass
from typing import TYPE_CHECKING

from based_utils.calx import FULL_CIRCLE, Bounds, CyclicBounds, frange, trim
from based_utils.colors import HSLuv

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True)
class InterpolationParams:
    n: int = 19
    inclusive: bool = False
    dynamic_range: float = 0


def _shades_2(
    color_1: HSLuv, color_2: HSLuv, *, params: InterpolationParams
) -> Iterator[HSLuv]:
    dark_color, bright_color = sorted([color_1, color_2])

    l_dark = Bounds(dark_color.lightness, 0).interpolate(params.dynamic_range)
    l_bright = Bounds(bright_color.lightness, 1).interpolate(params.dynamic_range)

    hue_bounds = CyclicBounds(dark_color.hue, bright_color.hue, FULL_CIRCLE)
    saturation_bounds = Bounds(dark_color.saturation, bright_color.saturation)
    lightness_bounds = Bounds(l_dark, l_bright)

    for lightness in frange(params.n, inclusive=params.inclusive):
        f = lightness_bounds.inverse_interpolate(lightness, inside=False)
        hue = hue_bounds.interpolate(f) % FULL_CIRCLE
        saturation = trim(saturation_bounds.interpolate(f), 0, 1)
        yield HSLuv(lightness, saturation, hue)


def generate_shades(
    color_1: HSLuv, color_2: HSLuv = None, *, params: InterpolationParams
) -> Iterator[HSLuv]:
    return (
        _shades_2(color_1, color_2, params=params)
        if color_2
        else color_1.shades(params.n, inclusive=params.inclusive)
    )
