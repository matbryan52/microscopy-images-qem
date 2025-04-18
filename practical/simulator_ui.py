import numpy as np
import panel as pn
pn.extension("floatpanel")

from libertem_ui.figure import ApertureFigure
from libertem_ui.display.display_base import Rectangles
from simulator import STEMImageSimulator, PointYX


def simulator_ui(simulator: STEMImageSimulator):
    survey_shape = (512, 512)
    survey_dwell_time = 0.000_001
    survey = simulator.survey_image(survey_shape, survey_dwell_time)
    survey_fig = (
        ApertureFigure
        .new(
            survey.astype(np.float32),
            title="Survey image",
        )
    )

    rectangles = (
        Rectangles
        .new()
        .empty()
        .on(survey_fig.fig)
        .editable(selected=True, num_objects=1)
    )

    survey_button = pn.widgets.Button(
        name="Update survey",
        button_type="primary",
    )
    survey_fig._toolbar.append(survey_button)

    def update_survey(*e):
        survey = simulator.survey_image(survey_shape, survey_dwell_time)
        survey_fig.update(
            survey.astype(np.float32)
        )

    update_cb = pn.state.add_periodic_callback(
        update_survey,
        period=2000,
        start=False,
    )

    def toggle_update(*e):
        if update_cb.running:
            return
        update_cb.start()

    survey_button.on_click(toggle_update)


    scan_step_input = pn.widgets.FloatInput(
        name="Scan step", value=0.5, start=0.01, end=20., step=0.01, width=100, align='end'
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

    scan_button = pn.widgets.Button(
        name="Scan",
        button_type="success",
    )
    survey_fig._toolbar.append(scan_button)
    survey_fig._toolbar.append(scan_step_input)
    survey_fig._outer_toolbar.height = 100

    def do_scan(*e):
        sh, sw = survey_shape
        data = rectangles.cds.data
        if len(data["cx"]) == 0:
            return
        cx, cy = data["cx"][0], data["cy"][0]
        w, h = abs(data["w"][0]), abs(data["h"][0])
        ex_y, ex_x = simulator._extent
        xscale = ex_x / sw
        yscale = ex_y / sh
        extent = PointYX(yscale * h, xscale * w)
        top = (cy * yscale) - extent.y / 2
        left = (cx * xscale) - extent.x / 2
        tl = PointYX(top, left)
        scan_step = scan_step_input.value
        scan_shape = (int(extent.y / scan_step), int(extent.x / scan_step))
        scan_img = simulator._scan(
            tl, extent, scan_shape, 0.001
        )
        scan_fig.update(scan_img.astype(np.float32))

    scan_button.on_click(do_scan)

    return pn.Row(
        survey_fig.layout,
        scan_fig.layout,
    )


if __name__ == "__main__":
    import pathlib
    rootdir = pathlib.Path(__file__).parent
    image = np.load(rootdir / "particles.npy")
    size = 1000
    simulator = STEMImageSimulator(image, (size, size), drift_speed=10.)
    simulator_ui(simulator).show()
