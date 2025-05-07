import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from libertem_ui.display.display_base import PointSet
from skimage.transform import PolynomialTransform, warp
from bokeh.models.tools import LassoSelectTool

pn.extension('floatpanel')


good_src = np.asarray(
[[381.67089227,  23.70877662],
 [381.67089227, 108.09512397],
 [381.67089227, 209.91666848],
 [387.93459271, 294.30301583],
 [104.67747757,  62.06620465],
 [110.24519868, 120.6484682 ],
 [119.9886822,  283.84191463],
 [120.68460473, 340.33193516],
 [205.5921527,  205.03484402],
 [ 12.81030663,  50.21027002],
 [ 26.03363005, 276.86781869]]
)
good_dst = np.asarray(
[[380.97491293,  23.70877662],
 [390.02241711, 108.79251934],
 [405.33362174, 207.82445393],
 [422.73276439, 292.90819665],
 [117.20482165,  61.36879505],
 [124.16444462, 119.95104437],
 [158.96261629, 285.23673381],
 [171.48996037, 343.12157354],
 [232.73472206, 205.03481555],
 [ 20.92411902,  52.07106795],
 [ 61.52772425, 276.86781869],]
)


custom_style = {
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}

img1 = np.load(rootdir / "overview_100K_binned.npy").astype(np.float32)
h, w = img1.shape

def inverse_transform(coords):
    row, col = coords[:, 0], coords[:, 1]
    return np.stack((row + 45 - ((col * 0.95 / h) ** 1.65) * 100., col), axis=1)

img1 = warp(img1, inverse_transform)
img1 = img1[35:430, 23:460]

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

fig2 = (
    ApertureFigure
    .new(
        img1,
        title='Polynomial transform',
        maxdim=470,
    )
)
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right.pop(0)

select_tool = LassoSelectTool(renderers="auto")
fig2.fig.tools.append(select_tool)

pointset = (
    PointSet
    .new()
    .empty()
    .on(fig2.fig)
    .editable(
        selected=True,
    )
)
pointset.points.fill_color = "orange"

pointset_dest = (
    PointSet
    .new()
    .empty()
    .on(fig2.fig)
    .editable(
        selected=False,
        tag_name="destination",
    )
)
pointset_dest.points.fill_color = "chartreuse"

def _update_warped(*e):
    new_cx = np.asarray(pointset.cds.data["cx"]).ravel()
    new_cy = np.asarray(pointset.cds.data["cy"]).ravel()
    if new_cy.size == 0:
        return
    dst = np.stack([new_cx, new_cy], axis=-1)

    old_cx = np.asarray(pointset_dest.cds.data["cx"]).ravel()
    old_cy = np.asarray(pointset_dest.cds.data["cy"]).ravel()
    if old_cy.size == 0:
        return
    src = np.stack([old_cx, old_cy], axis=-1)

    if new_cy.size != old_cy.size:
        return

    # Could add different transform estimates here
    tform = PolynomialTransform()
    tform.estimate(src, dst)

    out = warp(img1, tform)
    fig2.update(out)


def _show_original(*e):
    fig2.update(img1)


run_btn = pn.widgets.Button(name="Run", button_type="success", styles=custom_style, width=125)
run_btn.on_click(_update_warped)
original_btn = pn.widgets.Button(name="Show original", button_type="default", styles=custom_style, width=125)
original_btn.on_click(_show_original)
load_btn = pn.widgets.Button(name="Load", button_type="default", styles=custom_style, width=75)
clear_btn = pn.widgets.Button(name="Reset", button_type="warning", styles=custom_style, width=125)

def clear_cb(*e):
    pointset.clear()
    pointset_dest.clear()
    fig2.update(img1)

def load_cb(*e):
    fig2.update(img1)
    pointset.update(x=good_dst[:, 0], y=good_dst[:, 1])
    pointset_dest.update(x=good_src[:, 0], y=good_src[:, 1])

clear_btn.on_click(clear_cb)
load_btn.on_click(load_cb)
fig2._toolbar.append(run_btn)
fig2._toolbar.append(clear_btn)
fig2._toolbar.append(original_btn)
fig2._toolbar.append(load_btn)

pn.Column(
    fig2.layout,
).servable("transform-polynomial")
