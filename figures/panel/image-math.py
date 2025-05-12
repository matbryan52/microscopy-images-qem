import time
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from skimage.io import imread
import pathlib
rootdir = pathlib.Path(__file__).parent

pn.extension('codeeditor', 'floatpanel')


img = imread(rootdir.parent / "Region-ReferenceImage-Graphene.png", as_gray=True).astype(np.float32)
img = img[:800, ...]
h, w = img.shape

cat = imread(rootdir.parent / "cat.png", as_gray=True).astype(np.float32)
cat = cat[25: 25 + h, 150:150 + w]

fig1 = (
    ApertureFigure
    .new(
        img,
        title='Input image',
        downsampling=False,
    )
)
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.
fig1.fig.right[0].width = 30
fig2 = (
    ApertureFigure
    .new(
        (-1 * img).astype(np.float32),
        title='Output',
        downsampling=False,
    )
)    
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.
fig2.fig.right[0].width = 30

py_code = """def image_function(img):
    return -1 * img


#  img ** 2  |  np.log(0.01 + img)  |  img * range(w)
"""
editor = pn.widgets.CodeEditor(
    value=py_code,
    sizing_mode='stretch_width',
    language='python',
    height=125,
    on_keyup=False,
    stylesheets=["""
.ace_editor{
    font-size: 17px;
}
"""],
    margin=(20, 5, 5, 5),
)
button = pn.widgets.Button(
    name="RUN",
    button_type="success",
    width=200,
)
error_text = pn.widgets.StaticText(
    value="",
    width=200,
)

def run_callback(*e):
    try:
        button.button_type="warning"
        locals_dict = {}
        exec(editor.value, globals(), locals_dict)
        image_function = locals_dict["image_function"]
        result = image_function(img.copy())
        if not isinstance(result, np.ndarray):
            raise RuntimeError("Not an array")
        if result.ndim != 2:
            raise RuntimeError("Not 2D")
        if np.iscomplexobj(result):
            raise RuntimeError("Result is complex")
        fig2.update(result.astype(np.float32))
        time.sleep(0.2)
        button.button_type="success"
        error_text.value = ""
    except Exception as ex:
        error_text.value = str(ex)
        button.button_type="danger"

editor.param.watch(run_callback, "value")
button.on_click(run_callback)

fig1._outer_toolbar.height = 0
fig2._outer_toolbar.height = 0

pn.Column(
    pn.Row(
        editor,
        pn.Column(
            button,
            error_text,
        ),
        width_policy="max",
    ),
    pn.Row(
        fig1.layout,
        fig2.layout,
        align=("center", "center"),
        width_policy="max",       
    )
).servable("image-math")
