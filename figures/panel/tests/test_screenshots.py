import pytest
import pathlib
rootdir = pathlib.Path(__file__).parent
from playwright.sync_api import Page
from PIL.Image import open as imopen


@pytest.fixture(autouse=True, scope="session")
def clear_folder():
    for f in rootdir.iterdir():
        if f.suffix == ".png":
            f.unlink()


@pytest.mark.parametrize(
    "address",
    (    
        ("http://localhost:9091/aliasing", "bk-Row"),
        ("http://localhost:9091/brightness-contrast", "bk-Row"),
        ("http://localhost:9091/colour-uniformity", "bk-panel-models-layout-Column"),
        ("http://localhost:9091/complex-image", "bk-Row"),
        ("http://localhost:9091/connected-components", "bk-Row"),
        ("http://localhost:9091/film-particles", "bk-Row"),
        ("http://localhost:9091/fourier-filtering", "bk-panel-models-layout-Column"),
        ("http://localhost:9091/gamma-log", "bk-Row"),
        ("http://localhost:9091/image-math", "bk-panel-models-layout-Column"),
        ("http://localhost:9091/interpolation-sampling", "bk-Row"),
        ("http://localhost:9091/morphological", "bk-Row"),
        ("http://localhost:9091/points-align", "bk-panel-models-layout-Column"),
        ("http://localhost:9091/stem-moire", "bk-Row"),
        ("http://localhost:9091/thresholding", "bk-Row"),
        ("http://localhost:9091/transform-affine", "bk-panel-models-layout-Column"),
        ("http://localhost:9091/transform-nonuniform", "bk-panel-models-layout-Column"),
        ("http://localhost:9091/transparency", "bk-panel-models-layout-Column"),
        # ("http://localhost:9091/warp-polar", "bk-Row"),
    )
)
def test_screenshots(address, page: Page):
    address, cl = address
    page.goto(address, wait_until="networkidle")
    frame = page.locator(f'[class="{cl}"]').first
    name = address.split("/")[-1]
    fpath = rootdir / f"{name}.png"
    frame.screenshot(
        path=fpath,
        omit_background=True,
        # full_page=False,
    )

    im = imopen(fpath)
    im.getbbox()
    im2 = im.crop(im.getbbox())
    im2.save(fpath)
