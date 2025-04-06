import matplotlib.pyplot as plt
import numpy as np
import panel as pn
from libertem_ui.figure import figure
from libertem_ui.display.display_base import Curve, PointSet
from numpy.typing import NDArray


def sinc_interpolation(x: NDArray, s: NDArray, u: NDArray) -> NDArray:
    """Whittaker–Shannon or sinc or bandlimited interpolation.
    Args:
        x (NDArray): signal to be interpolated, can be 1D or 2D
        s (NDArray): time points of x (*s* for *samples*) 
        u (NDArray): time points of y (*u* for *upsampled*)
    Returns:
        NDArray: interpolated signal at time points *u*
    Reference:
        This code is based on https://gist.github.com/endolith/1297227
        and the comments therein.
    """
    sinc_ = np.sinc((u - s[:, None])/(s[1]-s[0]))
    return np.dot(x, sinc_)


high_num = 1024
freq = 16
high_xvals = np.linspace(0., 1., num=high_num, endpoint=True)
high_yvals = np.sin(2 * np.pi * freq * high_xvals)

low_num = 48
low_xvals = np.linspace(0., 1., num=low_num, endpoint=True)
low_yvals = np.sin(2 * np.pi * freq * low_xvals)
interpolated = sinc_interpolation(low_yvals, low_xvals, high_xvals)

fig1 = figure()
fig1.frame_height = 400
fig1.frame_width = 700
fig1.background_fill_alpha = 0.
fig1.border_fill_color = None
fig1.x_range.range_padding = 0.
fig1.y_range.range_padding = 0.
fig1.xaxis.axis_label = "Time"
fig1.yaxis.axis_label = "Level"
fig1.y_range.start = -1
fig1.y_range.end = 1

true_curve = (
    Curve
    .new()
    .from_vectors(
        high_xvals,
        high_yvals,
    )
    .on(fig1)
)
true_curve.glyph.line_width = 2

interp_curve = (
    Curve
    .new()
    .from_vectors(
        high_xvals,
        interpolated,
    )
    .on(fig1)
)
interp_curve.glyph.line_color = "orange"
interp_curve.glyph.line_width = 3


samples = (
    PointSet
    .new()
    .from_vectors(low_xvals, low_yvals)
    .on(fig1)
)
samples.points.fill_color = None
samples.points.line_color = "orange"
samples.points.marker = "circle"


samples_slider = pn.widgets.IntSlider(name="Sampling rate", value=low_num, start=4, end=128)
info_md = pn.pane.Markdown(object=f"Percent of signal frequency = {100 * samples_slider.value / freq:.1f} %")


def reinterpolate(*e):
    low_num = samples_slider.value
    low_xvals = np.linspace(0., 1., num=low_num, endpoint=True)
    low_yvals = np.sin(2 * np.pi * freq * low_xvals)
    interpolated = sinc_interpolation(low_yvals, low_xvals, high_xvals)
    interp_curve.update(high_xvals, interpolated)
    samples.update(x=low_xvals, y=low_yvals)
    info_md.object = f"Percent of signal frequency = {100 * low_num / freq:.1f} %"

samples_slider.param.watch(reinterpolate, "value")

pn.Row(
    pn.Column(
        samples_slider,
        info_md,
        align=("center", "center"),
    ),
    pn.pane.Bokeh(fig1),
).servable("aliasing")
