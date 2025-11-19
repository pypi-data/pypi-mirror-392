from dataclasses import dataclass
from typing import TYPE_CHECKING

from based_utils.calx import (
    CyclicInterpolationBounds,
    InterpolationBounds,
    fractions,
    interpolate,
    trim,
)
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
    c_dark, c_bright = sorted([color_1, color_2])

    dynamic_range = params.dynamic_range
    l_dark = interpolate(dynamic_range, start=c_dark.lightness, end=0)
    l_bright = interpolate(dynamic_range, start=c_bright.lightness, end=1)
    lightness_bounds = InterpolationBounds(l_dark, l_bright)

    saturation_bounds = InterpolationBounds(c_dark.saturation, c_bright.saturation)
    hue_bounds = CyclicInterpolationBounds(c_dark.hue, c_bright.hue)

    for lightness in fractions(params.n, inclusive=params.inclusive):
        f = lightness_bounds.inverse_interpolate(lightness, inside=False)
        hue = hue_bounds.interpolate(f)
        saturation = trim(saturation_bounds.interpolate(f))
        yield HSLuv(lightness, saturation, hue)


def generate_shades(
    color_1: HSLuv, color_2: HSLuv = None, *, params: InterpolationParams
) -> Iterator[HSLuv]:
    return (
        _shades_2(color_1, color_2, params=params)
        if color_2
        else color_1.shades(params.n, inclusive=params.inclusive)
    )
