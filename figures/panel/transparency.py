import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from skimage.io import imread
from bokeh.models import Slider, CustomJS
from skimage.transform import SimilarityTransform
from skimage.color import rgb2hsv

base_img = imread(rootdir / "base-image.png", as_gray=True)
# element_img = imread(rootdir / "edx-image.png")
b_img = (imread(rootdir / "Maps-R.png", as_gray=True)* 255).astype(np.uint8)
g_img = (imread(rootdir / "Maps-G.png", as_gray=True)* 255).astype(np.uint8)
r_img = (imread(rootdir / "Maps-B.png", as_gray=True)* 255).astype(np.uint8)
# element_img = np.zeros((*b_img.shape, 3))

element_img = np.stack(((r_img * 0.5).astype(np.uint8), g_img, b_img), axis=-1)

eh, ey, _ = element_img.shape
element_img_hsv = rgb2hsv(element_img)

corresponding = {
    (146, 39): (576,332),
    (144, 189): (574, 672),
    (68, 90): (404, 451),
    (83, 126): (438, 544),
    (186, 124): (671, 526),
}
tfor = SimilarityTransform()
tfor.estimate(
    np.asarray(tuple(corresponding.keys())),
    np.asarray(tuple(corresponding.values()))
)

ty, tx, _ = tfor.params @ np.asarray((0, 0, 1))
teh, tew, _ = tfor.params @ np.asarray((eh, ey, 1))
teh -= ty
tew -= tx

alpha_1 = (element_img_hsv[..., -1] * 255).astype(np.uint8)
# alpha_1 = np.ones(black_mask.shape, np.uint8) * 255
element_img = np.concatenate((element_img, alpha_1[..., np.newaxis]), axis=-1)

fig = (
    ApertureFigure
    .new(
        base_img,
        tools=False,
        maxdim=450,
        title="EDS Transparency"
    )
)

fig.fig.background_fill_alpha = 0.
fig.fig.border_fill_color = None
# fig1.fig.right[0].background_fill_alpha = 0.
fig._outer_toolbar.height = 0


h, w, _ = element_img.shape
element_img = element_img.view(np.uint32).reshape(h, w).copy()
img_rgba_renderer = fig.fig.image_rgba(
    image=[element_img], x=tx, y=ty, dw=tew, dh=teh, global_alpha=0.
)
img_rgba = img_rgba_renderer.glyph

alpha_slider = Slider(
    title="EDS Alpha",
    start=0.,
    end=1.,
    value=img_rgba.global_alpha,
    step=0.01,
    syncable=False,
    margin=(10, 10),
    align="end",
)
callback = CustomJS(args={'glyph': img_rgba, "other_glyph": fig.im.im}, code="""
glyph.global_alpha = cb_obj.value;
other_glyph.global_alpha = 1 - (cb_obj.value / 2);
""")
alpha_slider.js_on_change('value', callback)
# fig._toolbar.append(pn.HSpacer(max_width=150))
fig.layout.append(alpha_slider)


fig.fig.toolbar_location = "below"
fig.layout.servable("transparency")
