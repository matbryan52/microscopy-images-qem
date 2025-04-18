import numpy as np
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
