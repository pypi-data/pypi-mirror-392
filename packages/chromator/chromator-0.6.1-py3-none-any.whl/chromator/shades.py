from dataclasses import dataclass
from typing import TYPE_CHECKING

from based_utils.calx import Bounds, CyclicBounds
from based_utils.colors import HSLuv

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True)
class InterpolationParams:
    step: int = 5
    inclusive: bool = False
    dynamic_range: float = 0


def _shades_1(color: HSLuv, *, params: InterpolationParams) -> Iterator[HSLuv]:
    s = params.step if params.inclusive else 0
    for lightness in range(params.step - s, 100 + s, params.step):
        yield HSLuv(lightness, color.saturation, color.hue)


def _shades_2(
    color_1: HSLuv, color_2: HSLuv, *, params: InterpolationParams
) -> Iterator[HSLuv]:
    dark_color, bright_color = sorted([color_1, color_2])

    l_dark = Bounds(dark_color.lightness, 0).interpolate(params.dynamic_range)
    l_bright = Bounds(bright_color.lightness, 100).interpolate(params.dynamic_range)

    hue_bounds = CyclicBounds(dark_color.hue, bright_color.hue, 360)
    saturation_bounds = Bounds(dark_color.saturation, bright_color.saturation)
    lightness_bounds = Bounds(l_dark, l_bright)

    s = params.step if params.inclusive else 0
    for lightness in range(params.step - s, 100 + s, params.step):
        f = lightness_bounds.inverse_interpolate(lightness)
        hue = hue_bounds.interpolate(f)
        saturation = saturation_bounds.interpolate(f)
        yield HSLuv(lightness, saturation, hue)


def generate_shades(
    color_1: HSLuv, color_2: HSLuv = None, *, params: InterpolationParams
) -> Iterator[HSLuv]:
    return (
        _shades_2(color_1, color_2, params=params)
        if color_2
        else _shades_1(color_1, params=params)
    )
