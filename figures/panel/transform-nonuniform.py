import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from libertem_ui.display.display_base import PointSet
from skimage.transform import PiecewiseAffineTransform, warp

pn.extension('floatpanel')


size = 64
img1 = (np.linalg.norm(np.mgrid[-size: size, -size: size], axis=0) < 25).astype(np.float32)

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
fig1.fig.right[0].background_fill_alpha = 0.

yy, xx = img1.shape
step = 16
src_pts = np.mgrid[:yy + 1:step, :xx + 1:step].reshape(2, -1)
cy, cx = src_pts
cy = cy.ravel().tolist()
cx = cx.ravel().tolist()
src_pts = src_pts.T[:, ::-1]

fig2 = (
    ApertureFigure
    .new(
        img1,
        title='Transformed',
        maxdim=400,
    )
)
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.

pointset = (
    PointSet
    .new()
    .from_vectors(cx, cy)
    .on(fig2.fig)
    .editable(
        selected=True,
    )
)

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

pn.Row(
    fig1.layout,
    pn.layout.HSpacer(max_width=50),
    fig2.layout,
    align="center",
    sizing_mode="stretch_both",
).servable("transform-nonuniform")
