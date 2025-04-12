import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from skimage.io import imread
from bokeh.models import Slider, CustomJS

base_img = imread(rootdir / "base-image.png", as_gray=True)
# print(base_img.shape)
element_img = imread(rootdir / "edx-image.png")
# print(element_img.dtype)


black_mask = (element_img == 0).sum(axis=-1) == 0
alpha_1 = ((1 - black_mask.astype(int)) * 255).astype(np.uint8)
alpha_1 = np.ones(black_mask.shape, np.uint8) * 255
element_img = np.concatenate((element_img, alpha_1[..., np.newaxis]), axis=-1)

fig = (
    ApertureFigure
    .new(
        base_img,
        tools=False,
        maxdim=450,
        title="EDX Transparency"
    )
)

fig.fig.background_fill_alpha = 0.
fig.fig.border_fill_color = None
# fig1.fig.right[0].background_fill_alpha = 0.
fig._outer_toolbar.height = 0


h, w, _ = element_img.shape
element_img = element_img.view(np.uint32).reshape(h, w).copy()
img_rgba_renderer = fig.fig.image_rgba(
    image=[element_img], x=0, y=210, dw=900, dh=900, global_alpha=0.
)
img_rgba = img_rgba_renderer.glyph

alpha_slider = Slider(
    title="EDX Alpha",
    start=0.,
    end=1.,
    value=img_rgba.global_alpha,
    step=0.01,
    syncable=False,
    margin=(10, 10),
    align="end",
)
callback = CustomJS(args={'glyph': img_rgba}, code="""glyph.global_alpha = cb_obj.value;""")
alpha_slider.js_on_change('value', callback)
# fig._toolbar.append(pn.HSpacer(max_width=150))
fig.layout.append(alpha_slider)


fig.fig.toolbar_location = "below"
fig.layout.servable("transparency")
