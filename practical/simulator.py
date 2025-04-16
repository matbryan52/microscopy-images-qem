from scipy.stats.qmc import PoissonDisk
import numpy as np
import time
import tqdm.auto as tqdm
from typing import NamedTuple, TypeAlias
from skimage.transform import AffineTransform
from scipy.interpolate import RegularGridInterpolator, CubicSpline

from libertem_ui.figure import ApertureFigure
from libertem_ui.display.display_base import Cursor, Rectangles
import panel as pn
pn.extension("floatpanel")

Degrees: TypeAlias = float
Distance: TypeAlias = float

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


class ShapeYX(NamedTuple):
    y: int
    x: int


class DriftState(NamedTuple):
    start: complex
    vector: complex
    alpha: float
    beta: float
    timestep: float


def get_drift_curve(start: complex, vector: complex, alpha: float, beta: float, timestep: float, time: float):
    times = np.arange(np.ceil(time / timestep).astype(int) + 1) * timestep
    speed_randomness = np.random.normal(scale=alpha, size=(len(times),)) * timestep
    angle_randomness = np.random.normal(scale=alpha * 100, size=(len(times),)) * timestep
    speed_mult = 1 + speed_randomness
    angle_change = np.clip(beta * angle_randomness, -beta, beta)
    angle_change = np.cumsum(angle_change)
    initial_speed = np.abs(vector)
    initial_angle = np.angle(vector)
    positions = np.cumsum(
        initial_speed * speed_mult * np.exp(1j * (initial_angle + angle_change))
    ) + start
    return (
        DriftState(positions[-1], positions[-1] - positions[-2], alpha, beta, timestep),
        CubicSpline(times, positions.astype(np.complex64).view(np.float32).reshape(positions.size, 2)),
    )


class STEMImageSimulator:
    def __init__(self, image: np.ndarray, extent_yx: tuple[float, float]):
        self._shape = ShapeYX(*image.shape)
        self._extent = PointYX(*extent_yx)
        cy = np.linspace(0, self._extent.y, num=image.shape[0], endpoint=True)
        cx = np.linspace(0, self._extent.x, num=image.shape[1], endpoint=True)
        self._current = 100000  # electron / ms
        self._interpolator = RegularGridInterpolator(
            (cy, cx),
            image,
            bounds_error=False,
            fill_value=None,
        )
        self._defocus = 0.
        drift_speed = 0.0001  # np.random.uniform(0.001, 0.002)
        drift_angle = np.random.uniform(-np.pi, np.pi)
        self._drift = DriftState(
            0 + 0j,
            drift_speed * np.exp(1j * drift_angle),
            alpha=1.,
            beta=0.1,
            timestep=0.001,
        )

    def _apply_defocus(self, point: PointYX):
        df = self._defocus
        yvals = np.tile(point.y[:, np.newaxis], (1, 5))
        xvals = np.tile(point.x[:, np.newaxis], (1, 5))
        yvals += np.asarray([0, -df, -df, df, df])
        xvals += np.asarray([0, -df, df, -df, df])
        return PointYX(yvals.ravel(), xvals.ravel())

    def _apply_drift(self, point: PointYX, indices: np.ndarray, dwell_time: float):
        scan_times = indices * dwell_time
        assert dwell_time >= self._drift.timestep
        max_time = scan_times.max()
        self._drift, drift_interpolant = get_drift_curve(*self._drift, max_time)
        drift = drift_interpolant(scan_times)
        drift = PointYX(drift[:, 1], drift[:, 0])
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


def generate_particle():
    from ase.cluster import Octahedron, Icosahedron
    option = np.random.choice([1])
    symbol = ("Au",)  #, "Cu", "Ag", "Al")
    if option == 0:
        atoms = Octahedron(
            np.random.choice(symbol),
            np.random.randint(5, 13),
            cutoff=np.random.choice([0, 1, 2]),
        )
    elif option == 1:
        atoms = Icosahedron(
            np.random.choice(symbol),
            noshells=np.random.choice(np.arange(4, 9)),
        )
    atoms.euler_rotate(
        *np.random.uniform(-180, 180, size=(3,))
    )
    return atoms


def simulator_ui(simulator: STEMImageSimulator):
    survey_shape = (512, 512)
    survey_dwell_time = 0.001
    survey = simulator.survey_image(survey_shape, survey_dwell_time)
    survey_fig = (
        ApertureFigure
        .new(
            survey.astype(np.float32),
            title="Survey image",
        )
    )
    cursor = (
        Cursor
        .new()
        .from_pos(
            *tuple(a / 2 for a in survey_shape)
        )
        .on(survey_fig.fig)
        .editable(selected=True)
    )

    survey_button = pn.widgets.Button(
        name="Update survey",
        button_type="primary",
    )
    survey_fig._toolbar.append(survey_button)

    def update_survey(*e):
        survey = simulator.survey_image(survey_shape, survey_dwell_time)
        survey_fig.update(
            survey.astype(np.float32)
        )

    update_cb = pn.state.add_periodic_callback(
        update_survey,
        period=2000,
        start=False,
    )

    def toggle_update(*e):
        if update_cb.running:
            return
        update_cb.start()

    survey_button.on_click(toggle_update)


    scan_shape_input = pn.widgets.IntInput(
        name="Scan size", value=100, start=2, end=1000, step=10, width=100, align='end'
    )
    scan_step_input = pn.widgets.FloatInput(
        name="Scan step", value=0.5, start=0.01, end=20., step=0.01, width=100, align='end'
    )

    scan_shape = (scan_shape_input.value, scan_shape_input.value)
    scan = np.zeros(scan_shape, dtype=np.float32)
    scan_fig = (
        ApertureFigure
        .new(
            scan,
            title="Scan",
            downsampling=False,
        )
    )

    scan_button = pn.widgets.Button(
        name="Scan",
        button_type="success",
    )
    survey_fig._toolbar.append(scan_button)
    survey_fig._toolbar.append(scan_shape_input)
    survey_fig._toolbar.append(scan_step_input)
    survey_fig._outer_toolbar.height = 100

    def do_scan(*e):
        sh, sw = survey_shape
        x, y = cursor.current_pos()
        ex_y, ex_x = simulator._extent
        tl = PointYX((y / sh) * ex_y, (x / sw) * ex_x)
        scan_shape = (scan_shape_input.value, scan_shape_input.value)
        scan_img = simulator.scan(tl, scan_step_input.value, scan_shape, 0., 0.005)
        scan_fig.update(scan_img.astype(np.float32))

    scan_button.on_click(do_scan)

    return pn.Row(
        survey_fig.layout,
        scan_fig.layout,
    )


if __name__ == "__main__":
    import pathlib
    rootdir = pathlib.Path(__file__).parent
    import matplotlib.pyplot as plt
    from skimage.io import imread

    # state = DriftState(
    #     0 + 0j,
    #     np.random.uniform(-5, 5) + np.random.uniform(-5, 5) * 1j,
    #     alpha=20.,
    #     beta=0.1,
    #     timestep=0.001,
    # )
    # max_time = 100.
    # state, interpolant = get_drift_curve(*state, time=max_time)
    # positions = interpolant(np.linspace(0., 1., num=int(max_time)))
    # drift = PointYX(positions[:, 1], positions[:, 0])
    # plt.plot(drift.x, drift.y, 'x-')
    # plt.show()

    # image = imread(pathlib.Path(__file__).parent / "overview_100K.tif", as_gray=True)
    # simulator = STEMImageSimulator(image, (100., 100.))

    # grid, scan = simulator.scan(
    #     (40, 40), 0.1, (100, 200), 20, 0.001, with_grid=True,
    # )
    # fig, (ax1, ax2) = plt.subplots(1, 2)
    # ax1.imshow(
    #     image,
    #     origin='upper',
    #     extent=(0, simulator._extent[1], simulator._extent[0], 0),
    #     cmap="gray",
    # )
    # ax1.plot(grid.x, grid.y, 'rx')
    # ax2.imshow(scan, cmap="gray")
    # plt.show()

    if False:
        atoms = []
        size = 1000
        num_particles = 30
        rng = np.random.default_rng()
        engine = PoissonDisk(
            d=2,
            radius=60,
            rng=rng,
            l_bounds=(0, 0),
            u_bounds=(size,) * 2,
        )
        sample = engine.random(num_particles)
        for (dy, dx) in sample:
            at = generate_particle()
            # positions = at.get_positions()
            # minx, miny, _ = positions.min(axis=0)
            # maxx, maxy, _ = positions.max(axis=0)
            # h, w = maxy - miny, maxx - minx
            at.translate([dy, dx, 0.])
            atoms.append(at)

        atoms_combined = atoms[0]
        for a in atoms[1:]:
            atoms_combined.extend(a)
        xy_vac = 20
        atoms_combined.center(xy_vac)
        positions = atoms_combined.get_positions()
        _, _, minz = positions.min(axis=0)
        _, _, maxz = positions.max(axis=0)
        size = size + (xy_vac * 2)

        import abtem
        sampling = 0.25  # A / px
        shape = (size / sampling,) * 2  #px
        potential = abtem.Potential(
            atoms_combined,
            gpts=shape,
            slice_thickness=5,
            periodic=False,
            projection="infinite",
        )
        tstart = time.time()
        potential_array = potential.build(lazy=False)
        array = potential_array.array.sum(axis=0)
        m5, m95 = np.percentile(array.ravel(), (0.5, 99.5))
        array -= m5
        array /= (m95 - m5)
        array = np.clip(array, 0., 1.)

        measurements = abtem.measurements.Images(
            array,
            sampling=sampling,
        )
        filtered_measurements = measurements.gaussian_filter(0.75)

        # plt.imshow(filtered_measurements.array, cmap="gray")
        # plt.show()
        image = filtered_measurements.array
        np.save(rootdir / "particles.npy", image)

    # image = imread(rootdir / "overview_100K.tif", as_gray=True)
    image = np.load(rootdir / "particles.npy")
    image = np.clip(image, 0.03, np.inf)
    size = 1000
    simulator = STEMImageSimulator(image, (size, size))

    # tl = PointYX(70, 560)
    # survey = simulator.survey_image((512, 512), 0.001)
    # grid, scan = simulator.scan(
    #     tl, 0.5, (200, 200), 0.005, with_grid=True,
    # )
    # fig, (ax1, ax2) = plt.subplots(1, 2)
    # ax1.imshow(
    #     survey,
    #     origin='upper',
    #     extent=(0, simulator._extent[1], simulator._extent[0], 0),
    #     cmap="gray",
    # )
    # ax1.set_title(f"Survey image {survey.shape}")
    # # ax1.plot(grid.x, grid.y, 'rx')
    # ax2.imshow(scan, cmap="gray")
    # ax2.set_title(f"Scan {scan.shape}")
    # plt.show()

    simulator_ui(simulator).show()
