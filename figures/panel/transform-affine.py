import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from libertem_ui.applications.image_transformer import ImageTransformer

pn.extension('floatpanel', 'mathjax')


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

it = ImageTransformer(img1)

fig2 = (
    ApertureFigure
    .new(
        it.get_transformed_image(),
        title='Transformed',
        maxdim=400,
    )
)
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.

def format_transform():
    tform = it.get_combined_transform().params
    return f"""
$$\\begin{{matrix}}
{tform[0, 0]:.2f} & {tform[0, 1]:.2f} & {tform[0, 2]:.2f} \\\\
{tform[1, 0]:.2f} & {tform[1, 1]:.2f} & {tform[1, 2]:.2f} \\\\
{tform[2, 0]:.2f} & {tform[2, 1]:.2f} & {tform[2, 2]:.2f} \\\\
\\end{{matrix}}
$$"""

transform_md = pn.pane.Markdown(object=format_transform())

def update_figures():
    fig2.update(it.get_transformed_image())
    transform_md.object = format_transform()


scale_btn = pn.widgets.Button(name="Scale")
def scale_cb(*e):
    it.xy_scale_about_center(xscale=np.random.uniform(low=0.9, high=1.1), yscale=np.random.uniform(low=0.5, high=1.5))
    update_figures()
    

scale_btn.on_click(scale_cb)
rotate_btn = pn.widgets.Button(name="Rotate")
def rotate_cb(*e):
    it.rotate_about_center(rotation_degrees=np.random.uniform(low=-20, high=20))
    update_figures()

rotate_btn.on_click(rotate_cb)
flip_btn = pn.widgets.Button(name="Flip")
def flip_cb(*e):
    # it.()
    update_figures()

flip_btn.on_click(flip_cb)
shear_btn = pn.widgets.Button(name="Shear")
def shear_cb(*e):
    it.shear(xshear=0., yshear=0.)
    update_figures()

shear_btn.on_click(shear_cb)
shift_btn = pn.widgets.Button(name="Shift")
def shift_cb(*e):
    it.translate(xshift=np.random.uniform(low=-20, high=20), yshift=np.random.uniform(low=-20, high=20))
    update_figures()

shift_btn.on_click(shift_cb)
clear_btn = pn.widgets.Button(name="Clear")
def clear_cb(*e):
    it.clear_transforms()
    update_figures()

clear_btn.on_click(clear_cb)

pn.Column(
    # pn.pane.Markdown(object=text),
    pn.Row(
        scale_btn,
        rotate_btn,
        flip_btn,
        shear_btn,
        shift_btn,
        clear_btn,
        transform_md,
    ),
    pn.Row(
        fig1.layout,
        pn.layout.HSpacer(max_width=50),
        fig2.layout,
        align="center",
        sizing_mode="stretch_both",
    )
).servable("transform-affine")
