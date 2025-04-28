import abtem
from ase.build import graphene
import matplotlib.pyplot as plt

unitcell = 2.504
nx = 100
unstretched = graphene(a=unitcell, size=(nx, 100, 1))
stretched = graphene(a=unitcell * 1.05, size=(100, 100, 1))
stretched.translate(((nx + 0.5) * unitcell, -0.5 * unitcell, 0))
unstretched.extend(stretched)
xy_vac = 3
unstretched.center(xy_vac)

# abtem.show_atoms(
#     unstretched,
#     plane="xy",  # show a view perpendicular to the 'xy' plane
#     scale=0.5,  # scale atoms to 0.5 of their covalent radii; default is 0.75
# );
# plt.show()

sampling = 0.25  # A / px
potential = abtem.Potential(
    unstretched,
    sampling=sampling,
    # slice_thickness=5,
    # periodic=False,
    projection="infinite",
).build(lazy=False)

potential.show()
