import numpy as np
from itertools import pairwise
import time
import operator
import tqdm.auto as tqdm
from typing import NamedTuple, TypeAlias
from skimage.transform import AffineTransform
from scipy.interpolate import RegularGridInterpolator
from bezier_curve import generate_curve

Degrees: TypeAlias = float
Distance: TypeAlias = float


class YX(NamedTuple):
    y: float | np.ndarray
    x: float | np.ndarray

    def __binary_op(self, op, val):
        if isinstance(val, YX):
            return YX(
                y=op(self.y, val.y),
                x=op(self.x, val.x),
            )
        else:
            return YX(
                y=op(self.y, val),
                x=op(self.x, val),
            )

    def __mul__(self, val: float | int):
        return self.__binary_op(operator.mul, val)

    def __truediv__(self, val: float | int):
        return self.__binary_op(operator.truediv, val)

    def __mod__(self, val: float | int):
        return self.__binary_op(operator.mod, val)

    def __add__(self, val: float | int):
        return self.__binary_op(operator.add, val)

    def __sub__(self, val: float | int):
        return self.__binary_op(operator.sub, val)

    def to_int(self):
        if self.is_scalar():
            return YX(int(self.y), int(self.x))
        else:
            return YX(self.y.astype(int), self.x.astype(int))

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

    def rotate(self, angle: Degrees, about: 'YX'):
        if angle == 0.:
            return self
        about = YX(*about)
        assert about.is_scalar()
        translated = self - about
        transform = AffineTransform(rotation=np.deg2rad(angle)).params[:2, :2]
        points = translated.asarray(yx=False)
        rotated = points @ transform
        return YX(
            y=rotated[:, 1], x=rotated[:, 0]
        ) + about


class ScanDef(NamedTuple):
    tl: YX
    extent: YX
    shape: YX

    @property
    def scaling(self) -> YX:
        """
        Scale factors in Distance / Pixel
        """
        return self.extent / self.shape

    def to_continuous(self, point: YX) -> YX:
        """
        Convert from survey pixel units to continuous units
        """
        point = YX(*point)
        return self.tl + (point * self.scaling)

    def to_pixels(self, point: YX) -> YX:
        """
        Convert from continuous units to survey pixel
        """
        point = YX(*point)
        return (point - self.tl) / self.scaling


class STEMImageSimulator:
    def __init__(
        self,
        image: np.ndarray,
        extent_yx: tuple[float, float],
        current: int = 10_000_000,  # electron / s,
        drift_speed: float = 1.,
        defocus: float = 0.,
    ):
        self._shape = YX(*image.shape)
        self._extent = YX(*extent_yx)
        cy = np.linspace(0, self._extent.y, num=image.shape[0], endpoint=True)
        cx = np.linspace(0, self._extent.x, num=image.shape[1], endpoint=True)
        self._interpolator = RegularGridInterpolator(
            (cy, cx),
            image,
            bounds_error=False,
            fill_value=None,
        )
        self._rng = np.random.default_rng()

        survey_fraction = 0.8
        self._survey_def = ScanDef(
            tl = self._extent * ((1 - survey_fraction) / 2),
            extent = self._extent * survey_fraction,
            shape=YX(512, 512),
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

    def _apply_defocus(self, point: YX):
        df = self._defocus
        yvals = np.tile(point.y[:, np.newaxis], (1, 5))
        xvals = np.tile(point.x[:, np.newaxis], (1, 5))
        yvals += np.asarray([0, -df, -df, df, df])
        xvals += np.asarray([0, -df, df, -df, df])
        return YX(yvals.ravel(), xvals.ravel())

    def _apply_drift(self, point: YX, indices: np.ndarray, dwell_time: float):
        scan_times = self.rel_time() + indices * dwell_time
        drift = self._drift_for_times(scan_times)
        drift = YX(drift.imag, drift.real)
        return point + drift

    def _wrap_coordinate(self, yx: YX):
        return yx % self._extent

    @staticmethod
    def _get_grid(tl: YX, extent: YX, shape: YX, rotation: Degrees):
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
        grid = YX(yy.ravel(), xx.ravel())
        grid = grid.rotate(rotation, tl)
        return grid, indices

    def _sample(self, grid_coords: YX, dwell_time: float):
        scattering_factor = self._interpolator(grid_coords)
        samples = self._rng.poisson(
            lam=dwell_time * scattering_factor * self._current
        )
        return samples

    @property
    def survey(self) -> ScanDef:
        """
        The definition of the survey image coordinate system
        with methods to convert from survey pixels to continuous units
        """
        return self._survey_def

    def survey_image(self, dwell_time: float, wait: bool = False):
        """
        Acquire a new survey image with the given dwell time
        """
        return self._scan(
            **self.survey._asdict(),
            dwell_time=dwell_time,
            wait="Survey" if wait else wait,
        )

    def _scan(
        self,
        *,
        tl: YX,
        extent: YX,
        shape: YX,
        dwell_time: float,
        rotation: Degrees = 0.,
        wait: bool | str = False,
    ) -> np.ndarray:
        # could add a scan pattern option
        tstart = time.perf_counter()
        shape = YX(*shape)
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
            grid = YX(grid.y[::5], grid.x[::5])
        image = image.reshape(shape)
        if wait:
            tspent = time.perf_counter() - tstart
            npts = indices.size
            true_time = npts * dwell_time
            effective_dwell_time = max(0, (true_time - tspent) / npts)
            step = 256
            bar = tqdm.tqdm(total=npts, desc=wait if isinstance(wait, str) else "Scanning")
            for _ in range(0, npts, step):
                bar.update(step)
                time.sleep(effective_dwell_time * step)
        else:
            self._tstart -= indices.size * dwell_time
        return image

    def scan(
        self,
        centre: YX,  # float-pixel survey coordinates of scan grid centre
        scan_shape: YX,  # shape of desired scan in pixels
        scan_step: Distance,  # stepsize of desired scan in continuous units
        dwell_time: float,
        rotation: Degrees = 0.,
        with_grid: bool = False,
        wait: bool = False,
    ):
        """
        Acquire a scan image
        """
        centre_scan = self.survey.to_continuous(centre)
        extent = YX(*scan_shape) * scan_step
        tl = centre_scan - (extent / 2)
        image = self._scan(
            tl=tl,
            extent=extent,
            shape=scan_shape,
            dwell_time=dwell_time,
            rotation=rotation,
            wait="Scanning" if wait else wait,
        )
        if with_grid:
            grid, _ = self._get_grid(tl, extent, scan_shape, rotation)
            return image, grid - self.survey.tl  # in continuous coords
        return image


if __name__ == "__main__":
    import pathlib
    rootdir = pathlib.Path(__file__).parent
    import matplotlib.pyplot as plt

    sim_data = np.load(rootdir / "particles.npz")
    image = sim_data["data"]
    extent = sim_data["extent"]
    simulator = STEMImageSimulator(image, extent, drift_speed=0.)

    survey = simulator.survey_image(0.000_001, wait=True)
    h, w = survey.shape
    scan_centre = YX(h // 2, w // 2)
    scan_shape = YX(512, 512)
    scan, grid = simulator.scan(
        scan_centre, scan_shape, 1.5, 0.00001, rotation=10, with_grid=True, wait=True
    )

    fig, (ax1, ax2) = plt.subplots(1, 2)
    extent = simulator.survey.extent
    ax1.imshow(
        survey,
        origin='upper',
        extent=(0, extent.x, extent.y, 0),
        cmap="gray",
    )
    ax1.set_title(f"Survey image {survey.shape}")
    ax1.plot(grid.x, grid.y, 'rx')
    ax2.imshow(scan, cmap="gray")
    plt.show()
