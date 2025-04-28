import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from libertem_ui.display.display_base import PointSet
from skimage.transform import PiecewiseAffineTransform, warp
from bokeh.models.tools import LassoSelectTool

pn.extension('floatpanel')

custom_style = {
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}

img1 = np.load(rootdir / "overview_100K_binned.npy").astype(np.float32)

fig1 = (
    ApertureFigure
    .new(
        img1,
        title='Input',
        maxdim=400,
    )
)
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right.pop(0)

yy, xx = img1.shape
step = 64
src_pts = np.mgrid[:yy + 1:step, :xx + 1:step].reshape(2, -1)
cy, cx = src_pts
cy = cy.ravel().tolist()
cx = cx.ravel().tolist()
src_pts = src_pts.T[:, ::-1]

fig2 = (
    ApertureFigure
    .new(
        img1,
        title='Piecewise-affine',
        maxdim=470,
    )
)
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right.pop(0)

select_tool = LassoSelectTool(renderers="auto")
fig2.fig.tools.append(select_tool)

hide_points = pn.widgets.Toggle(
    name="Hide grid",
    button_type='success',
    styles=custom_style,
    width=125,
)

pointset = (
    PointSet
    .new()
    .from_vectors(cx, cy)
    .on(fig2.fig)
    .editable(
        add=False,
        selected=True,
    )
)
pointset.points.fill_color = "orange"

def _update_warped(attr, old, new):
    new_cx = np.asarray(pointset.cds.data["cx"]).ravel()
    new_cy = np.asarray(pointset.cds.data["cy"]).ravel()
    dst = np.stack([new_cx, new_cy], axis=-1)

    # Could add different transform estimates here
    tform = PiecewiseAffineTransform()
    tform.estimate(src_pts, dst)

    out = warp(img1, tform.inverse)
    fig2.update(out)

pointset.cds.on_change("data", _update_warped)

clear_btn = pn.widgets.Button(name="Reset", button_type="warning", styles=custom_style, width=125)

def clear_cb(*e):
    pointset.update(x=cx, y=cy)

def do_hide_points(e):
    pointset.set_visible(not e.new)

hide_points.param.watch(do_hide_points, "value")

clear_btn.on_click(clear_cb)
fig2._toolbar.append(clear_btn)
fig2._toolbar.append(hide_points)

pn.Column(
    fig2.layout,
).servable("transform-nonuniform")
