import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from libertem_ui.applications.image_transformer import ImageTransformer

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
fig1._outer_toolbar.height = 0

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
fig2.fig.right.pop(0)
fig2._outer_toolbar.height = 0

def format_transform():
    tform = it.get_combined_transform().params
    return f"""
| {tform[0, 0]:.2f} | {tform[0, 1]:.2f} | {tform[0, 2]:.2f} | **x** | 
|:--:|:--:|:--:|:--:|
| **{tform[1, 0]:.2f}** | **{tform[1, 1]:.2f}** | **{tform[1, 2]:.2f}** | **y** | 
| **{tform[2, 0]:.0f}** | **{tform[2, 1]:.0f}** | **{tform[2, 2]:.0f}** | **1** | 
"""

def format_summary():
    transform = it.get_combined_transform()
    scale_x, scale_y = transform.scale
    trans_x, trans_y = transform.translation
    return f"""| Rotation | Scale   | Shear    | Translation   |
| -------- | ------- | -------- | -------       |
| {np.rad2deg(transform.rotation):.1f}  | ({scale_x:.3f}, {scale_y:.3f}) | {transform.shear:.2f}  | ({trans_x:.1f}, {trans_y:.1f}) |
"""  # noqa

transform_md = pn.pane.Markdown(object=format_transform(), styles=custom_style)
summary_md = pn.pane.Markdown(object=format_summary(), styles=custom_style)

def update_figures():
    fig2.update(it.get_transformed_image())
    transform_md.object = format_transform()
    summary_md.object = format_summary()

common_kwargs = dict(
    button_type="primary",
    width=100,
    margin=(2, 2),
    styles=custom_style,
)

scale_up_btn = pn.widgets.Button(name="Scale up", **common_kwargs)
scale_down_btn = pn.widgets.Button(name="Scale down", **common_kwargs)

def scale_down_cb(*e):
    it.xy_scale_about_center(xscale=1.1, yscale=1.1)
    update_figures()

def scale_up_cb(*e):
    it.xy_scale_about_center(xscale=0.9, yscale=0.9)
    update_figures()


scale_down_btn.on_click(scale_down_cb)
scale_up_btn.on_click(scale_up_cb)

rotate_btn_ac = pn.widgets.Button(name="Rotate \u21B6", **common_kwargs)
rotate_btn_c = pn.widgets.Button(name="Rotate \u21B7", **common_kwargs)

def rotate_cb_ac(*e):
    it.rotate_about_center(rotation_degrees=5)
    update_figures()

def rotate_cb_c(*e):
    it.rotate_about_center(rotation_degrees=-5)
    update_figures()

rotate_btn_ac.on_click(rotate_cb_ac)
rotate_btn_c.on_click(rotate_cb_c)

# flip_x_btn = pn.widgets.Button(name="Flip-X", **common_kwargs)
# flip_y_btn = pn.widgets.Button(name="Flip-Y", **common_kwargs)

# def flip_x_cb(*e):
#     # it.()
#     update_figures()

# def flip_y_cb(*e):
#     # it.()
#     update_figures()

# flip_x_btn.on_click(flip_x_cb)
# flip_y_btn.on_click(flip_y_cb)

shear_x_pos_btn = pn.widgets.Button(name="Shear-X +", **common_kwargs)
shear_y_pos_btn = pn.widgets.Button(name="Shear-Y +", **common_kwargs)

def shear_x_pos_cb(*e):
    it.shear(xshear=0.05)
    update_figures()

def shear_y_pos_cb(*e):
    it.shear(yshear=0.05)
    update_figures()

shear_x_pos_btn.on_click(shear_x_pos_cb)
shear_y_pos_btn.on_click(shear_y_pos_cb)

shear_x_neg_btn = pn.widgets.Button(name="Shear-X -", **common_kwargs)
shear_y_neg_btn = pn.widgets.Button(name="Shear-Y -", **common_kwargs)

def shear_x_neg_cb(*e):
    it.shear(xshear=-0.05)
    update_figures()

def shear_y_neg_cb(*e):
    it.shear(yshear=-0.05)
    update_figures()

shear_x_neg_btn.on_click(shear_x_neg_cb)
shear_y_neg_btn.on_click(shear_y_neg_cb)

shift_x_pos_btn = pn.widgets.Button(name="Shift-X →", **common_kwargs)
shift_y_pos_btn = pn.widgets.Button(name="Shift-Y ↓", **common_kwargs)

def shift_x_pos_cb(*e):
    it.translate(xshift=-10, yshift=0.)
    update_figures()

def shift_y_pos_cb(*e):
    it.translate(xshift=0., yshift=-10)
    update_figures()

shift_x_pos_btn.on_click(shift_x_pos_cb)
shift_y_pos_btn.on_click(shift_y_pos_cb)

shift_x_neg_btn = pn.widgets.Button(name="Shift-X ←", **common_kwargs)
shift_y_neg_btn = pn.widgets.Button(name="Shift-Y ↑", **common_kwargs)

def shift_x_neg_cb(*e):
    it.translate(xshift=10, yshift=0.)
    update_figures()

def shift_y_neg_cb(*e):
    it.translate(xshift=0., yshift=10)
    update_figures()

shift_x_neg_btn.on_click(shift_x_neg_cb)
shift_y_neg_btn.on_click(shift_y_neg_cb)

clear_btn = pn.widgets.Button(name="Clear", button_type="warning")

def clear_cb(*e):
    it.clear_transforms()
    update_figures()

clear_btn.on_click(clear_cb)

pn.Column(
    pn.Row(
        pn.Column(scale_up_btn, scale_down_btn, clear_btn, margin=(5, 2)),
        pn.Column(rotate_btn_ac, rotate_btn_c, margin=(5, 2)),
        pn.Column(shear_x_pos_btn, shear_x_neg_btn, margin=(5, 2)),
        pn.Column(shear_y_pos_btn, shear_y_neg_btn, margin=(5, 2)),
        pn.Column(shift_x_pos_btn, shift_x_neg_btn, margin=(5, 2)),
        pn.Column(shift_y_pos_btn, shift_y_neg_btn, margin=(5, 2)),
        transform_md,
        summary_md,
    ),
    pn.Row(
        fig1.layout,
        pn.HSpacer(max_width=30),
        fig2.layout,
        # align="center",
        # sizing_mode="stretch_both",
    )
).servable("transform-affine")
