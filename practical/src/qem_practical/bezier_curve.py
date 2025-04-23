import numpy as np
from typing import TypeAlias

Degrees: TypeAlias = float

class QuadBezier:
    def __init__(self, p0: complex, p1: complex, p2: complex):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

    def coordinate_at(self, tvals: float | np.ndarray):
        return self.p1 + (1 - tvals)**2 * (self.p0-self.p1) + tvals**2 * (self.p2 - self.p1)

    def evaluate(self, granuality: int = 100):
        tvals = np.linspace(0, 1., num=granuality)
        return tvals, self.coordinate_at(tvals)

    def arc_length(self):
        tvals, xy = self.evaluate(granuality=1000)
        vectors = np.diff(xy, 1)
        lengths = np.abs(vectors)
        return tvals, xy, lengths.sum()


def continuing_angle(angle, max_change: Degrees = 5):
    max_change = np.deg2rad(max_change)
    delta_angle = np.clip(
        np.random.normal(scale=0.5 * max_change),
        -max_change,
        max_change,
    )
    return angle + delta_angle


def random_between(start: complex, end: complex, new_length: bool = None) -> complex:
    length = np.abs(end - start)
    angle = np.angle(end - start)
    new_angle = continuing_angle(angle)
    delta_angle = new_angle - angle
    if new_length is None:
        new_length = np.random.uniform(0.33, 0.66) * length * np.cos(delta_angle)
    return start + new_length * np.exp(1j * new_angle)


def continue_line(start: complex, end: complex, min_length: float = 0.):
    length = np.abs(end - start)
    angle = np.angle(end - start)
    length_factor = np.random.uniform(0.8, 1.2)
    new_length = length_factor * length
    new_length = max(min_length, new_length)
    return end + new_length * np.exp(1j * angle)


def generate_curve(start: complex = 0j, scale: float = 1.):
    p0 = start
    p2 = p0 + np.exp(1j * np.random.uniform(-np.pi, np.pi))
    p1 = random_between(p0, p2)
    while True:
        yield QuadBezier(
            p0 * scale, p1 * scale, p2 * scale,
        )
        p0 = p2
        p1 = continue_line(p1, p2, min_length=0.4)
        p2 = random_between(p0, p1, new_length=1.)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for ix, curve in enumerate(generate_curve(scale=0.1)):
        _, B = curve.evaluate()
        ax.plot(B.real, B.imag, 'k-')
        if ix > 40:
            break
    plt.show()
