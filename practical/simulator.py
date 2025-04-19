import numpy as np
import time
import operator
from scipy import constants
import tqdm.auto as tqdm
from typing import NamedTuple, TypeAlias, Self
from scipy.interpolate import RegularGridInterpolator
from bezier_curve import generate_curve

Degrees: TypeAlias = float
NanoMetres: TypeAlias = float
NMPerSecond: TypeAlias = float
Seconds: TypeAlias = float
PicoAmps: TypeAlias = float
ELECTRON_PER_PA = 1e-12 * (1 / constants.e)


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

    def __mul__(self, val: float | int | Self):
        return self.__binary_op(operator.mul, val)

    def __truediv__(self, val: float | int | Self):
        return self.__binary_op(operator.truediv, val)

    def __floordiv__(self, val: float | int | Self):
        return self.__binary_op(operator.floordiv, val)

    def __mod__(self, val: float | int | Self):
        return self.__binary_op(operator.mod, val)

    def __add__(self, val: float | int | Self):
        return self.__binary_op(operator.add, val)

    def __sub__(self, val: float | int | Self):
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
        angle = np.deg2rad(angle)
        about = YX(*about)
        assert about.is_scalar()
        translated = self - about
        transform = np.asarray([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)],
        ])
        points = translated.asarray(yx=False)
        rotated = points @ transform
        return YX(
            y=rotated[:, 1], x=rotated[:, 0]
        ) + about


PixelShapeYX: TypeAlias = YX
PixelYX: TypeAlias = YX
NanoMetreShapeYX: TypeAlias = YX
NanoMetreYX: TypeAlias = YX
NanoMetrePerPixelYX: TypeAlias = YX


class ScanDef(NamedTuple):
    tl: NanoMetreYX
    extent: NanoMetreShapeYX
    shape: PixelShapeYX

    @property
    def scaling(self) -> NanoMetrePerPixelYX:
        """
        Scale factors in Distance / Pixel
        """
        return self.extent / self.shape

    def to_continuous(self, point: PixelYX) -> NanoMetreYX:
        """
        Convert from survey pixel to continuous units
        """
        point = YX(*point)
        return self.tl + (point * self.scaling)

    def to_pixels(self, point: NanoMetreYX) -> PixelYX:
        """
        Convert from continuous to survey pixel units
        """
        point = YX(*point)
        return (point - self.tl) / self.scaling


class STEMImageSimulator:
    def __init__(
        self,
        image: np.ndarray,
        extent_yx: NanoMetreShapeYX,
        current: PicoAmps = 10,
        drift_speed: NMPerSecond = 0.1,
        defocus: NanoMetres = 0.,
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
    
    def _drift_for_times(self, start: Seconds, number: int, step: Seconds):
        coordinates = []
        curve_idx, curve = self._drift_state
        int_tval = np.floor(start)
        num_in_curve = int(1. / step)
        tvals = np.linspace(0., 1., num=num_in_curve)
        start_in_curve = int((start % 1) * num_in_curve)
        while number > 0:
            if int_tval < curve_idx:
                raise RuntimeError("Cannot index into past")
            while int_tval > curve_idx:
                curve_idx, curve = next(self._drift_gen)
            assert int_tval == curve_idx
            rel_times = tvals[start_in_curve: min(num_in_curve, start_in_curve + number)]
            coordinates.append(
                curve.coordinate_at(rel_times)
            )
            int_tval += 1
            number -= rel_times.size
            start_in_curve = 0
        return np.concatenate(coordinates, axis=0)

    def _apply_defocus(self, point: YX):
        df = self._defocus
        yvals = np.tile(point.y[:, np.newaxis], (1, 5))
        xvals = np.tile(point.x[:, np.newaxis], (1, 5))
        yvals += np.asarray([0, -df, -df, df, df])
        xvals += np.asarray([0, -df, df, -df, df])
        return YX(yvals.ravel(), xvals.ravel())

    def _apply_drift(self, point: YX, dwell_time: float):
        drift = self._drift_for_times(self.rel_time(), point.x.size, dwell_time)
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
        grid = YX(yy.ravel(), xx.ravel())
        grid = grid.rotate(rotation, tl + extent / 2)
        return grid

    def _sample(self, grid_coords: YX, dwell_time: float):
        scattering_factor = self._interpolator(grid_coords)
        samples = self._rng.poisson(
            lam=scattering_factor * (self._current * dwell_time * ELECTRON_PER_PA)
        )
        return samples

    def _scan(
        self,
        *,
        tl: NanoMetreYX,
        extent: NanoMetreShapeYX,
        shape: PixelShapeYX,
        dwell_time: Seconds,
        rotation: Degrees = 0.,
        wait: bool | str = False,
    ) -> np.ndarray:
        # could add a scan pattern option
        tstart = time.perf_counter()
        shape = YX(*shape)
        grid = self._get_grid(tl, extent, shape, rotation)
        grid = self._apply_drift(grid, dwell_time)
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
        tspent = time.perf_counter() - tstart
        npts = grid.x.size
        true_time = npts * dwell_time
        time_to_wait = max(0, (true_time - tspent))
        if wait:
            effective_dwell_time = time_to_wait / npts
            step = 256
            bar = tqdm.tqdm(total=npts, desc=wait if isinstance(wait, str) else "Scanning")
            for _ in range(0, npts, step):
                bar.update(step)
                time.sleep(effective_dwell_time * step)
        else:
            self._tstart -= time_to_wait
        return image

    @property
    def survey(self) -> ScanDef:
        """
        Get the definition of the survey image coordinate system
        with methods to convert from survey pixels to continuous units
        """
        return self._survey_def

    def survey_image(self, dwell_time: Seconds, wait: bool = False):
        """
        Acquire a new survey image with the given dwell time
        """
        return self._scan(
            **self.survey._asdict(),
            dwell_time=dwell_time,
            wait="Survey" if wait else wait,
        )

    def scan(
        self,
        centre: PixelYX,
        scan_shape: PixelShapeYX,
        scan_step: NanoMetres,
        dwell_time: Seconds,
        rotation: Degrees = 0.,
        with_grid: bool = False,
        wait: bool = False,
    ) -> np.ndarray | tuple[np.ndarray, YX]:
        """
        Acquire a scan image centered at a specified point.

        Performs a raster scan over a rectangular region centered 
        at the given survey coordinates, with optional rotation. 
        The scan is defined by its shape (in pixels), step size (in nanometres), 
        and dwell time per pixel (in seconds).

        Parameters
        ----------
        centre : PixelYX
            The center of the scan grid in float-pixel survey coordinates.
        scan_shape : PixelShapeYX
            The dimensions (rows, columns) of the scan in pixels.
        scan_step : NanoMetres
            The distance between scan points in nanometres.
        dwell_time : Seconds
            The dwell time of each pixel
        rotation : Degrees, optional
            Angle to rotate the scan grid (default is 0 degrees). Positive is anticlockwise.
        with_grid : bool, optional
            If True, also return the grid coordinates used in the scan (default is False).
        wait : bool, optional
            If True, block execution for the duration of the scan as-if
            waiting for the real microscope (default is False).

        Returns
        -------
        image : ndarray
            The acquired scan image.
        grid : YX, optional
            The scan grid in survey continuous coordinates, only returned if `with_grid` is True.

        Notes
        -----
        The returned grid, if requested, is relative to the survey's top-left origin.
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
            grid = self._get_grid(tl, extent, scan_shape, rotation)
            return image, grid - self.survey.tl  # in continuous coords
        return image


if __name__ == "__main__":
    import pathlib
    rootdir = pathlib.Path(__file__).parent
    import matplotlib.pyplot as plt

    sim_data = np.load(rootdir / "particles.npz")
    image = sim_data["data"]
    data_extent = YX(*sim_data["extent"])
    print(f"Data shape: {image.shape}, extent {data_extent} nm")
    simulator = STEMImageSimulator(image, data_extent, drift_speed=0.1)

    survey = simulator.survey_image(0.000_001, wait=False)
    h, w = survey.shape
    scan_centre = YX(h // 2, w // 2)
    scan_shape = YX(512, 512)
    scan, grid = simulator.scan(
        scan_centre, scan_shape, 0.1, 0.00001, rotation=10, with_grid=True, wait=False
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
