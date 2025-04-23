import numpy as np
from ase.cluster import Octahedron, Icosahedron


def generate_particle():
    option = np.random.choice([1])
    symbol = ("Au",)  #, "Cu", "Ag", "Al")
    if option == 0:
        length = np.random.randint(8, 16)
        max_cutoff = (length - 1) // 2
        cutoff = np.random.randint(max(1, 3 * max_cutoff // 4), max_cutoff)
        atoms = Octahedron(
            np.random.choice(symbol),
            length,
            cutoff=cutoff,
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
