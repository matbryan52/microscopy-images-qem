import matplotlib.pyplot as plt
import numpy as np
import panel as pn
from libertem_ui.figure import figure
from libertem_ui.display.display_base import Curve, PointSet
from numpy.typing import NDArray
from bokeh.models import Legend


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
true_curve.glyph.line_color = "#f28e2b"
# true_curve.glyph.muted_alpha = 0.2

interp_curve = (
    Curve
    .new()
    .from_vectors(
        high_xvals,
        interpolated,
    )
    .on(fig1)
)
interp_curve.glyph.line_color = "#4e79a7"
interp_curve.glyph.line_width = 3
# interp_curve.glyph.muted_alpha = 0.2


samples = (
    PointSet
    .new()
    .from_vectors(low_xvals, low_yvals)
    .on(fig1)
)
samples.points.fill_color = None
samples.points.line_color = "#4e79a7"
samples.points.marker = "circle"
# samples.points.muted_alpha = 0.2


legend = Legend(
    items=[
        ("True signal",   list(true_curve.renderers_for_fig('curve', fig1))),
        ("Interpolated signal", list(interp_curve.renderers_for_fig('curve', fig1))),
        ("Samples", list(samples.renderers_for_fig('points', fig1)))
    ],
    location="top_right",
    click_policy="hide",
)
fig1.add_layout(legend, "center")

signal_choice = pn.widgets.CheckBoxGroup(
    name="Signal",
    value=[f"Sin(f)"],
    options=["Sin(f)", "Cos(f)", "Sin(1/2f)"],
    inline=True,
)
intepolation_choice = pn.widgets.RadioBoxGroup(name="Interpolation", value="Sinc()", options=["Linear", "Sinc()"], inline=True)
samples_slider = pn.widgets.IntSlider(name="Sampling rate", value=low_num, start=4, end=128)
info_md = pn.pane.Markdown(object=f"Percent of signal frequency = {100 * samples_slider.value / freq:.1f} %")


def sample(xvals):
    signals = signal_choice.value
    output = np.zeros_like(xvals)
    if "Sin(f)" in signals:
        output += np.sin(2 * np.pi * freq * xvals)
    if "Cos(f)" in signals:
        output += np.cos(2 * np.pi * freq * xvals)
    if "Sin(1/2f)" in signals:
        output += np.sin(2 * np.pi * 0.5 * freq * xvals)
    output /= output.max()
    return output


def signal_change(*e):
    new_sig = sample(high_xvals)
    true_curve.update(high_xvals, new_sig)


def reinterpolate(*e):
    interpolation = intepolation_choice.value
    low_num = samples_slider.value
    low_xvals = np.linspace(0., 1., num=low_num, endpoint=True)
    low_yvals = sample(low_xvals)
    if interpolation == "Linear":
        interp_curve.update(low_xvals, low_yvals)
    else:
        interpolated = sinc_interpolation(low_yvals, low_xvals, high_xvals)
        interp_curve.update(high_xvals, interpolated)
    samples.update(x=low_xvals, y=low_yvals)
    info_md.object = f"Percent of signal frequency = {100 * low_num / freq:.1f} %"

samples_slider.param.watch(reinterpolate, "value")
intepolation_choice.param.watch(reinterpolate, "value")
signal_choice.param.watch(reinterpolate, "value")
signal_choice.param.watch(signal_change, "value")

pn.Row(
    pn.Column(
        signal_choice,
        pn.Row(pn.widgets.StaticText(value="Interpolation:"), intepolation_choice),
        samples_slider,
        info_md,
        align=("center", "center"),
    ),
    pn.pane.Bokeh(fig1),
).servable("aliasing")
