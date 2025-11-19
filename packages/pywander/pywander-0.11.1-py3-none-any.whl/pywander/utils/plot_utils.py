#!/usr/bin/env python
# -*-coding:utf-8-*-


"""
matplotlib plot utils

pandas虽然也有绘图功能，但感觉让事情变得复杂了。就算是已经转成pandas那边的数据类型了，要绘图提出指定的数据也是很方便的。

约定都统一到matplotlib这边的绘图接口上。

约定本脚本所有绘图函数都需要指定ax
"""

import numpy as np
from abc import ABC, abstractmethod
import matplotlib.patches as mpatches


def _process_ax_args(ax, title='', x_label='', y_label='', x_lim=None, y_lim=None):
    # 标题
    if title:
        ax.set_title(title)

    # 设置x标签
    if x_label:
        ax.set_xlabel(x_label)

    # 设置y标签
    if y_label:
        ax.set_ylabel(y_label)

    # 设置x轴范围
    if x_lim is not None:
        ax.set_xlim(x_lim)

    # 设置y轴范围
    if y_lim is not None:
        ax.set_ylim(y_lim)


def line_plot(ax, x_values=None, y_values=None, title='', x_label='', y_label='', x_tick_labels=None, x_lim=None,
              y_lim=None, **kwargs):
    """
    一般数据绘图：直线图

    kwargs 各个参数参见 `matplotlib.lines.Line2D` 文档

    https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D

    matplotlib 推荐的风格
    """
    if x_values is None and y_values is None:
        raise Exception(f'x_values, y_values, 至少要给定一个')

    if x_values is None:
        x_values = np.arange(len(y_values))

    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    # 设置x标签
    if x_tick_labels is not None:
        ax.set_xticks(x_values)
        ax.set_xticklabels(x_tick_labels)

    ax.plot(x_values, y_values, **kwargs)


def scatter_plot(ax, x_values, y_values, title='', x_label='', y_label='', x_lim=None, y_lim=None, **kwargs):
    """
    一般数据绘图：散点图
    """
    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    ax.scatter(x_values, y_values, **kwargs)


def math_func_plot(ax, x_values, math_func, title='', x_label='', y_label='', x_lim=None, y_lim=None, **kwargs):
    """
    一般数据绘图：函数绘图
    """
    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    y_values = [math_func(x) for x in x_values]
    ax.grid(True)
    ax.scatter(x_values, y_values, **kwargs)


def image_plot(ax, image_data, cmap=None, interpolation=None, vmin=None, vmax=None, title='', x_label='', y_label='',
               x_lim=None, y_lim=None, **kwargs):
    """
    显示图片
    """
    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    ax.imshow(image_data, interpolation=interpolation, cmap=cmap, vmin=vmin, vmax=vmax, **kwargs)


def pie_plot(ax, values, title='', x_label='', y_label='', x_lim=None, y_lim=None, **kwargs):
    """
    一般数据绘图：绘制饼状图
    :return:
    """
    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    ax.pie(values, autopct='%2.0f%%', startangle=90, **kwargs)


class PlotType(ABC):
    """图形绘制基类，所有图形类型需继承此类并实现draw方法"""

    @abstractmethod
    def draw(self, ax, **kwargs):
        pass


class Grid(PlotType):
    """
    绘制网格线
    """

    def __init__(self, origin_min, origin_max, x_ticks=None, y_ticks=None, **kwargs):
        self.origin_min = origin_min
        self.origin_max = origin_max
        self.x_ticks = x_ticks  # x轴刻度（如5表示每隔5单位一个刻度）
        self.y_ticks = y_ticks  # y轴刻度
        self.kwargs = kwargs

    def draw(self, ax, **kwargs):
        combined_kwargs = {
            "linestyle": "--",
            "linewidth": 0.8,
            "color": "gray",
            "alpha": 0.7,
            **self.kwargs, **kwargs}

        ax.set_xlim(self.origin_min[0] - 1, self.origin_max[0] + 1)
        ax.set_ylim(self.origin_min[1] - 1, self.origin_max[1] + 1)

        # 自定义刻度（如果指定）
        if self.x_ticks is not None:
            ax.set_xticks(np.arange(
                self.origin_min[0] - 1,
                self.origin_max[0] + 1,
                self.x_ticks
            ))
        if self.y_ticks is not None:
            ax.set_yticks(np.arange(
                self.origin_min[1] - 1,
                self.origin_max[1] + 1,
                self.y_ticks
            ))

        ax.grid(True, **combined_kwargs)


class Points(PlotType):
    """绘制多个点"""

    def __init__(self, *vectors, **kwargs):
        self.vectors = vectors
        self.kwargs = kwargs  # 存储点样式参数

    def draw(self, ax, **kwargs):
        combined_kwargs = {**self.kwargs, **kwargs}
        x_values, y_values = zip(*self.vectors)
        ax.scatter(x_values, y_values, **combined_kwargs)


class Segments(PlotType):
    """绘制直线段"""

    def __init__(self, *vectors, **kwargs):
        self.vectors = vectors
        self.kwargs = kwargs  # 存储线样式参数

    def draw(self, ax, **kwargs):
        combined_kwargs = {**self.kwargs, **kwargs}
        x_values, y_values = zip(*self.vectors)
        ax.plot(x_values, y_values, **combined_kwargs)


class Arrow(PlotType):
    """绘制箭头（基于 mpatches.FancyArrowPatch 实现，默认带箭头）"""

    def __init__(self, start, end, arrowstyle="->,head_width=6,head_length=10", **kwargs):
        self.start = start  # 起点坐标 (x, y)
        self.end = end  # 终点坐标 (x, y)
        self.arrowstyle = arrowstyle  # 箭头样式（默认带箭头）
        self.kwargs = kwargs  # 其他样式参数

    def draw(self, ax, **kwargs):
        # 合并样式：默认样式 → 实例化样式 → 绘制时样式
        combined_kwargs = {
            "color": "black",  # 默认颜色
            "linewidth": 1.5,  # 默认线宽
            "arrowstyle": self.arrowstyle,  # 确保使用箭头样式
            **self.kwargs, **kwargs
        }
        # 创建带箭头的补丁
        arrow = mpatches.FancyArrowPatch(
            self.start,
            self.end,
            **combined_kwargs
        )
        ax.add_patch(arrow)


class Circle(PlotType):
    """绘制圆形"""

    def __init__(self, center, radius, **kwargs):
        self.center = center  # (x, y) 中心点
        self.radius = radius  # 半径
        self.kwargs = kwargs  # 存储圆形样式参数

    def draw(self, ax, **kwargs):
        combined_kwargs = {**self.kwargs, **kwargs}
        circle = mpatches.Circle(self.center, self.radius, **combined_kwargs)
        ax.add_patch(circle)


class Rectangle(PlotType):
    """绘制矩形"""

    def __init__(self, xy, width, height, **kwargs):
        self.xy = xy  # 左下角坐标 (x, y)
        self.width = width  # 宽度
        self.height = height  # 高度
        self.kwargs = kwargs  # 存储矩形样式参数

    def draw(self, ax, **kwargs):
        combined_kwargs = {**self.kwargs, **kwargs}
        rect = mpatches.Rectangle(self.xy, self.width, self.height, **combined_kwargs)
        ax.add_patch(rect)


class Ellipse(PlotType):
    """绘制椭圆（明确指定angle参数）"""

    def __init__(self, center, width, height, angle=0, **kwargs):
        self.center = center  # (x, y) 中心点
        self.width = width  # 水平轴长度
        self.height = height  # 垂直轴长度
        self.angle = angle  # 旋转角度（度）
        self.kwargs = kwargs  # 存储椭圆样式参数

    def draw(self, ax, **kwargs):
        combined_kwargs = {**self.kwargs, **kwargs}
        # 明确使用angle=self.angle传递参数
        ellipse = mpatches.Ellipse(
            self.center, self.width, self.height, angle=self.angle, **combined_kwargs
        )
        ax.add_patch(ellipse)


class Polygon(PlotType):
    """绘制多边形"""

    def __init__(self, *vectors, **kwargs):
        self.vectors = vectors  # 多边形顶点坐标
        self.kwargs = kwargs  # 存储多边形样式参数

    def draw(self, ax, **kwargs):
        combined_kwargs = {
            "fill": False,
            **self.kwargs, **kwargs
        }

        polygon = mpatches.Polygon(self.vectors, **combined_kwargs)
        ax.add_patch(polygon)


def draw(ax, *objects, **kwargs):
    """
    通用绘图接口
    """
    for obj in objects:
        if isinstance(obj, PlotType):
            obj.draw(ax, **kwargs)
        else:
            raise TypeError(f"不支持的绘制对象类型: {type(obj)}")


def set_matplotlib_support_chinese(font='SimHei'):
    """
    设置matplotlib支持中文
    :param font:
    :return:
    """
    from matplotlib import rcParams

    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'].insert_child(0, font)  # 插入中文字体
