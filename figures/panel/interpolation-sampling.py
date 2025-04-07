import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
import skimage.io as skio
from libertem_ui.applications.line_profile import sampling_tool

pn.extension('floatpanel')

img = skio.imread(rootdir / "tiled-roofing-new-roof.jpg", as_gray=True)
row, getter = sampling_tool(img, fig_kwargs=dict(title="Image"))

fig1 = row[0][-1]
fig1.object.background_fill_alpha = 0.
fig1.object.border_fill_color = None
fig1.object.right[0].background_fill_alpha = 0.
fig2 = row[1][-1].object
fig2.background_fill_alpha = 0.
fig2.border_fill_color = None

row.align="center"
row.sizing_mode="stretch_both"
row.servable("interpolation-sampling")
