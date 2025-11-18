"""
File: biomatplotlib.py
Description: Drawing aid library for matplotlib.
CreateDate: 2024/7/18
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import List, Literal, Union
from os import listdir
from math import trunc
from numpy import random
import matplotlib.axes
import matplotlib.colors as mc
import matplotlib.font_manager as fm
from matplotlib.pyplot import rcParams
from click import echo


def set_custom_font(font_name: str):
    path = '/'.join(__file__.split('/')[:-1]) + '/font'
    all_fonts = [i.split('.')[0] for i in listdir(path)]
    if font_name not in all_fonts:
        msg = (f"\033[33mWarning: {font_name} font not found. Available fonts: {' '.join(all_fonts)}\n"
               f"Try to use the system-provided fonts.\033[0m")
        echo(msg, err=True)
        rcParams['font.family'] = font_name
    else:
        font_path = f'{path}/{font_name}.ttf'
        fm.fontManager.addfont(font_path)
        rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()


def generate_unique_colors(num_colors: int) -> List[str]:
    """Randomly generates a specified number of non-redundant hexadecimal color codes."""

    def __generate_unique_colors(num_colors):
        colors = set()
        while len(colors) < num_colors:
            r, g, b = random.rand(3)
            color = (r, g, b)
            colors.add(color)
        return colors

    unique_colors = __generate_unique_colors(num_colors)
    hex_colors = [mc.to_hex(color) for color in unique_colors]
    return hex_colors


def format_xticks_by_kmg(
    axes: matplotlib.axes.Axes,
    min_tick: Union[int, float] = None,
    max_tick: Union[int, float] = None,
    tick_unit: Union[int, float] = None,
    decimals: int = 2,
    rotation: Union[int, float] = None,
    grid: bool = True,
    **kwargs
) -> matplotlib.axes.Axes:
    xticks = axes.get_xticks()
    min_x = trunc(float(min(xticks))) if min_tick is None else min_tick
    max_x = trunc(float(max(xticks))) if max_tick is None else max_tick
    yticks = axes.get_yticks()
    min_y = trunc(float(min(yticks)))
    max_y = trunc(float(max(yticks)))
    if max_x / 10 ** 3 <= 1000:
        step = 10 ** 3
        unit = 'Kb'
        step_unit = 10 ** 3
    elif max_x / 10 ** 6 <= 1000:
        step = 10 ** 6
        unit = 'Mb'
        step_unit = 10 ** 6
    else:
        step = 10 ** 9
        unit = 'Gb'
        step_unit = 10 ** 9
    if tick_unit is not None:
        step *= tick_unit
        step = trunc(step)
    x_ticks = [i for i in range(min_x, max_x - step, step)]
    x_ticks.append(max_x)
    s = f'%.{decimals}f'
    x_labels = [s % (i / step_unit) for i in range(min_x, max_x - step, step)]
    x_labels.append(s % (max_x / step_unit))
    axes.set_xticks(x_ticks, x_labels, rotation=rotation)
    axes.set_xlim([min_x, max_x])
    axes.set_xlabel(unit, loc='right')
    if grid:
        for x in x_ticks:
            axes.plot([x, x], [min_y - 1, max_y + 1], **kwargs)
    return axes


def rotate_ax_tick_labels(
    axes: matplotlib.axes.Axes,
    axis: Literal['x', 'y', 'both'],
    rotation: int = 0,
    fontproperties: dict = None
) -> matplotlib.axes.Axes:
    """Rotate coordinate axis tick labels and fix Unicode minus signs without changing the scale of the axes and their labels."""
    axis = axis.lower()
    for ax in (["x", "y"] if axis == "both" else [axis]):
        # Dynamically obtain tags and process Unicode negative signs
        labels = [t.get_text().replace("−", "-") for t in getattr(axes, f"get_{ax}ticklabels")()]
        # Dynamically set the scale and rotation Angle of the coordinate axes
        getattr(axes, f"set_{ax}ticks")(
            [float(label) for label in labels],
            labels=labels,
            rotation=rotation,
            fontproperties=fontproperties
        )
    return axes
