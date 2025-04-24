import numpy as np
import panel as pn
import humanize
from bokeh.models import LinearAxis, Range1d
from bokeh.plotting import figure
pn.extension("floatpanel")

from libertem_ui.figure import ApertureFigure, set_frame_height
from libertem_ui.display.display_base import Rectangles, Curve
from .simulator import STEMImageSimulator, YX

MAXDIM = 512


def add_cal_axes(fig, extent, label):
    yrange, xrange = extent.y, extent.x
    fig.extra_y_ranges['cal'] = Range1d(yrange, 0.)
    fig.extra_x_ranges['cal'] = Range1d(0., xrange)

    axy = LinearAxis(
        axis_label=label,
        y_range_name="cal",
    )
    fig.add_layout(axy, 'left')

    axx = LinearAxis(
        axis_label=label,
        x_range_name="cal",
    )
    fig.add_layout(axx, 'below')


def update_cal_axes(fig, extent):
    yrange, xrange = extent.y, extent.x
    fig.extra_y_ranges['cal'].start = yrange
    fig.extra_x_ranges['cal'].end = xrange


def simulator_ui(simulator: STEMImageSimulator):
    survey_dwell_time = 0.000_001
    survey = simulator.survey_image(survey_dwell_time)
    survey_fig = (
        ApertureFigure
        .new(
            survey.astype(np.float32),
            title="Survey image",
            maxdim=MAXDIM,
            downsampling=False,
        )
    )

    add_cal_axes(survey_fig.fig, simulator.survey.extent, "Survey (nm)")

    rectangles = (
        Rectangles
        .new()
        .empty()
        .on(survey_fig.fig)
        .editable(selected=True)
    )

    tools = rectangles.tools("rectangles", survey_fig.fig)
    tools[survey_fig.fig][0].num_objects = 1


    drift_fig = figure(title='Drift', match_aspect=True)
    drift_fig_pane = pn.pane.Bokeh(drift_fig)
    drift_curve = (
        Curve
        .new()
        .empty()
        .on(drift_fig)
    )
    drift_fig.xaxis.axis_label="x-drift (nm)"
    drift_fig.yaxis.axis_label="y-drift (nm)"
    drift_fig.y_range.flipped = True


    live_survey_button = pn.widgets.Toggle(
        name="Live survey",
        value=False,
        width_policy="max",
        button_type="warning",
    )
    single_survey = pn.widgets.Button(
        name="Single survey",
        disabled=False,
        button_type="success",
        width_policy="max",
    )
    live_survey_button.jslink(single_survey, **{"value": "disabled"})

    survey_spinner = pn.indicators.LoadingSpinner(
        value=False,
        width=35, height=35,
    )

    def update_survey(*e):
        try:
            survey_spinner.value = True
            survey = simulator.survey_image(survey_dwell_time, progress=False)
            survey_fig.update(
                survey.astype(np.float32)
            )
            drift_curve.update(
                xvals=simulator._drift_history["xvals"],
                yvals=simulator._drift_history["yvals"],
            )
        finally:
            survey_spinner.value = False

    update_cb = pn.state.add_periodic_callback(
        update_survey,
        period=1000,
        start=False,
    )

    def toggle_update(e):
        if e.new and not update_cb.running:
            update_cb.start()
            live_survey_button.name = "Stop..."
        elif not e.new and update_cb.running:
            update_cb.stop()
            live_survey_button.name = "Live survey"
        else:
            update_cb.stop()
            live_survey_button.value = False
            live_survey_button.name = "Live survey"

    live_survey_button.param.watch(toggle_update, "value")
    single_survey.on_click(update_survey)

    scan_step_input = pn.widgets.Select(
        name="Scan step (nm)",
        value="0.2",
        options=[
            "0.05", "0.1", "0.2", "0.3", "0.5", "0.7", "1.0"
        ],
        width_policy="max",
    )

    dwell_time_input = pn.widgets.Select(
        name="Dwell time (µs)",
        value="10",
        options=[
            "0.1", "1", "10", "100", "1000",
        ],
        width_policy="max",
    )

    scan_shape = (64, 64)
    scan = np.zeros(scan_shape, dtype=np.float32)
    scan_fig = (
        ApertureFigure
        .new(
            scan,
            title="Scan",
            downsampling=False,
        )
    )

    add_cal_axes(scan_fig.fig, simulator.survey.extent, "Scan (nm)")

    scan_button = pn.widgets.Button(
        name="Scan",
        button_type="success",
        width_policy="max",
    )
    live_survey_button.jslink(scan_button, **{"value": "disabled"})

    def do_scan(*e):
        data = rectangles.cds.data
        if len(data["cx"]) == 0:
            return
        cx, cy = data["cx"][0], data["cy"][0]
        w, h = abs(data["w"][0]), abs(data["h"][0])

        extent = YX(h, w) * simulator.survey.scaling
        scan_step = float(scan_step_input.value)
        scan_shape = (extent / scan_step).to_int()
        dwell_time = float(dwell_time_input.value) * 1e-6
        scan_img = simulator.scan(
            YX(cy, cx), scan_shape, scan_step, dwell_time,
            rotation=0, progress=False,
        )

        update_cal_axes(scan_fig.fig, extent)
        set_frame_height(scan_fig.fig, scan_img.shape, maxdim=MAXDIM)
        scan_fig.update(scan_img.astype(np.float32))

    scan_button.on_click(do_scan)

    survey_fig._outer_toolbar.height = 0
    scan_fig._outer_toolbar.height = 0

    def scan_info_str():
        stub = ""
        data = rectangles.cds.data
        if len(data["cx"]) == 0:
            return stub + """

No ROI defined
"""
        cx, cy = data["cx"][0], data["cy"][0]
        w, h = abs(data["w"][0]), abs(data["h"][0])        
        extent = YX(h, w) * simulator.survey.scaling
        scan_step = float(scan_step_input.value)
        scan_shape = (extent / scan_step).to_int()
        dwell_time = float(dwell_time_input.value) * 1e-6
        scan_time = np.prod(scan_shape) * dwell_time
        return stub + f"""

- Shape: {scan_shape[0]} x {scan_shape[1]} px
- Extent: {extent[0]:.1f} x {extent[1]:.1f} nm
- Duration {humanize.naturaldelta(scan_time, minimum_unit="microseconds")}
"""

    scan_info_md = pn.pane.Markdown(
        object=scan_info_str()
    )

    def _update_md(*e):
        scan_info_md.object = scan_info_str()

    def _update_md_bk(attr, old, new):
        scan_info_md.object = scan_info_str()

    scan_step_input.param.watch(_update_md, "value")
    dwell_time_input.param.watch(_update_md, "value")
    rectangles.cds.on_change("data", _update_md_bk)

    return pn.template.FastListTemplate(
        title="STEM Image Simulator",
        sidebar=[
            pn.pane.Markdown(object="## Survey"),
            pn.Row(
                live_survey_button,
                single_survey,
                survey_spinner,
                width_policy="max",
            ),
            pn.pane.Markdown(object=f"""
- Shape: {simulator.survey.shape[0]} x {simulator.survey.shape[1]} px
- Extent: {simulator.survey.extent[0]:.0f} x {simulator.survey.extent[1]:.0f} nm
- Dwell time: {humanize.naturaldelta(survey_dwell_time, minimum_unit='microseconds')}
- Duration {humanize.naturaldelta(survey_dwell_time * np.prod(simulator.survey.shape), minimum_unit='microseconds')}

## Scan"""),
            scan_step_input,
            dwell_time_input,
            scan_button,
            scan_info_md,
            pn.pane.Markdown(object="## Drift correction"),
        ],
        accent="#005da1",
        main=[
            pn.Row(
                survey_fig.layout,
                scan_fig.layout,
            ),
            drift_fig_pane,
        ],
        main_layout=None,
        theme_toggle=False,
    )
