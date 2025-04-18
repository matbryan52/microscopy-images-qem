import pathlib
import time
rootdir = pathlib.Path(__file__).parent
import numpy as np
import abtem
from scipy.stats.qmc import PoissonDisk
from ase.cluster import Octahedron, Icosahedron


def generate_particle():
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


if __name__ == "__main__":
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
    image = np.clip(image, 0.03, np.inf)
    np.save(rootdir / "particles.npy", image)
