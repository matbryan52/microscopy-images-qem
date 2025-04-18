import numpy as np
from itertools import pairwise
import time
import tqdm.auto as tqdm
from typing import NamedTuple, TypeAlias
from skimage.transform import AffineTransform
from scipy.interpolate import RegularGridInterpolator
from bezier_curve import generate_curve

Degrees: TypeAlias = float
Distance: TypeAlias = float


class ShapeYX(NamedTuple):
    y: int
    x: int


class PointYX(NamedTuple):
    y: float | np.ndarray
    x: float | np.ndarray

    def __sub__(self, other: 'PointYX'):
        return PointYX(
            self.y - other.y,
            self.x - other.x,
        )

    def __add__(self, other: 'PointYX'):
        return PointYX(
            self.y + other.y,
            self.x + other.x,
        )

    def asarray(self, yx: bool = True):
        array = (
            np.atleast_2d(
                np.stack((
                    np.asarray(self.y),
                    np.asarray(self.x),
                ), axis=-1)
            )
        )
        if yx:
            return array
        return array[:, ::-1]

    def is_scalar(self):
        return np.isscalar(self.x) and np.isscalar(self.y)

    def rotate(self, angle: Degrees, about: 'PointYX'):
        about = PointYX(*about)
        assert about.is_scalar()
        translated = self - about
        transform = AffineTransform(rotation=np.deg2rad(angle)).params[:2, :2]
        points = translated.asarray(yx=False)
        rotated = points @ transform
        return PointYX(
            y=rotated[:, 1], x=rotated[:, 0]
        ) + about


class STEMImageSimulator:
    def __init__(
        self,
        image: np.ndarray,
        extent_yx: tuple[float, float],
        current: int = 10_000_000,  # electron / s,
        drift_speed: float = 1.,
        defocus: float = 0.,
    ):
        self._shape = ShapeYX(*image.shape)
        self._extent = PointYX(*extent_yx)
        cy = np.linspace(0, self._extent.y, num=image.shape[0], endpoint=True)
        cx = np.linspace(0, self._extent.x, num=image.shape[1], endpoint=True)
        self._interpolator = RegularGridInterpolator(
            (cy, cx),
            image,
            bounds_error=False,
            fill_value=None,
        )

        self._current = current
        self._defocus = defocus

        self._tstart = time.time()
        self._drift_gen = self._curve_generator(drift_speed)
        _ = next(self._drift_gen)

    def rel_time(self):
        return time.time() - self._tstart

    def _curve_generator(self, speed: float = 1.):
        for curve_idx, curve in enumerate(generate_curve(scale=speed), start=-1):
            self._drift_state = curve_idx, curve
            yield self._drift_state
    
    @staticmethod
    def _split_at_integers(times):
        int_times = np.floor(times).astype(int)
        tvals, first_indices = np.unique(int_times, return_index=True)
        first_indices = first_indices.tolist() + [len(times)]
        rel_times = times - int_times
        for tval, (start, end) in zip(tvals, pairwise(first_indices)):
            yield tval, rel_times[start: end]

    def _drift_for_times(self, times: np.ndarray):
        coordinates = []
        curve_idx, curve = self._drift_state
        for int_tval, rel_times in self._split_at_integers(times):
            if int_tval < curve_idx:
                raise RuntimeError("Cannot index into past")
            while int_tval > curve_idx:
                curve_idx, curve = next(self._drift_gen)
            assert int_tval == curve_idx
            coordinates.append(curve.coordinate_at(rel_times))
        return np.concatenate(coordinates, axis=0)

    def _apply_defocus(self, point: PointYX):
        df = self._defocus
        yvals = np.tile(point.y[:, np.newaxis], (1, 5))
        xvals = np.tile(point.x[:, np.newaxis], (1, 5))
        yvals += np.asarray([0, -df, -df, df, df])
        xvals += np.asarray([0, -df, df, -df, df])
        return PointYX(yvals.ravel(), xvals.ravel())

    def _apply_drift(self, point: PointYX, indices: np.ndarray, dwell_time: float):
        scan_times = self.rel_time() + indices * dwell_time
        drift = self._drift_for_times(scan_times)
        drift = PointYX(drift.imag, drift.real)
        return point + drift

    def _wrap_coordinate(self, yx: PointYX):
        ey, ex = self._extent
        cy = yx.y
        cx = yx.x
        return PointYX(cy % ey, cx % ex)

    @staticmethod
    def _get_grid(tl: PointYX, extent: PointYX, shape: ShapeYX, rotation: Degrees):
        y0 = tl.y
        x0 = tl.x
        br = tl + extent
        y1 = br.y
        x1 = br.x
        h, w = shape
        y_coords = np.linspace(y0, y1, num=h, endpoint=True)
        x_coords = np.linspace(x0, x1, num=w, endpoint=True)
        xx, yy = np.meshgrid(x_coords, y_coords)
        indices = np.arange(xx.ravel().size)
        grid = PointYX(yy.ravel(), xx.ravel())
        grid = grid.rotate(rotation, tl)
        return grid, indices

    def _sample(self, grid_coords: PointYX, dwell_time: float):
        scattering_factor = self._interpolator(grid_coords)
        samples = np.random.poisson(
            lam=dwell_time * scattering_factor * self._current
        )
        return samples

    def survey_image(self, shape: ShapeYX, dwell_time: float, wait: bool = False):
        tl = PointYX(0., 0.)
        return self._scan(
            tl, self._extent, shape, dwell_time, wait=wait,
        )

    def _scan(
        self,
        tl: PointYX,
        extent: PointYX,
        shape: ShapeYX,
        dwell_time: float,
        rotation: Degrees = 0.,
        wait: bool = False,
        with_grid: bool = False,
    ) -> np.ndarray:
        # could add a scan pattern option
        shape = ShapeYX(*shape)
        grid, indices = self._get_grid(tl, extent, shape, rotation)
        grid = self._apply_drift(grid, indices, dwell_time)
        has_defocus = self._defocus > 0.
        if has_defocus:
            grid = self._apply_defocus(grid)
        grid = self._wrap_coordinate(grid)
        image = (
            self._sample(
                (grid.y, grid.x),
                dwell_time,
            )
        )
        if has_defocus:
            image = image.reshape(-1, 5).mean(axis=-1)
            grid = PointYX(grid.y[::5], grid.x[::5])
        image = image.reshape(shape)
        if wait:
            for _ in tqdm.trange(indices.size):
                time.sleep(dwell_time)
        else:
            self._tstart -= indices.size * dwell_time
        if with_grid:
            return grid, image
        return image

    def scan(
        self,
        tl: PointYX,
        scan_step: Distance,
        shape: ShapeYX,
        dwell_time: float,
        rotation: Degrees = 0.,
        wait: bool = False,
        with_grid: bool = False,
    ):
        shape = ShapeYX(*shape)
        tl = PointYX(*tl)
        extent = PointYX(shape.y * scan_step, shape.x * scan_step)
        return self._scan(
            tl, extent, shape, rotation, dwell_time, wait=wait, with_grid=with_grid
        )


if __name__ == "__main__":
    import pathlib
    rootdir = pathlib.Path(__file__).parent
    import matplotlib.pyplot as plt

    sim_data = np.load(rootdir / "particles.npz")
    image = sim_data["data"]
    extent = sim_data["extent"]
    simulator = STEMImageSimulator(image, extent, drift_speed=0.)

    tl = PointYX(70, 560)
    survey = simulator.survey_image((512, 512), 0.001)
    time.sleep(0.5)
    # grid, scan = simulator.scan(
    #     tl, 0.5, (200, 200), 0.005, with_grid=True,
    # )
    survey2 = simulator.survey_image((512, 512), 0.001)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.imshow(
        survey,
        origin='upper',
        extent=(0, simulator._extent[1], simulator._extent[0], 0),
        cmap="gray",
    )
    ax1.set_title(f"Survey image {survey.shape}")
    # ax1.plot(grid.x, grid.y, 'rx')
    ax2.imshow(survey2, cmap="gray")
    # ax2.set_title(f"Scan {scan.shape}")
    plt.show()

