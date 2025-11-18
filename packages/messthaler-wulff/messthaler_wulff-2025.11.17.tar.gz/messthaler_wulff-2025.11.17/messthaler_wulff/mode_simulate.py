import open3d as o3d

from .additive_simulation import SimpleNeighborhood, OmniSimulation
from .data import *
from .progress import ProgressBar


def plot_sim(sim):
    points = o3d.geometry.PointCloud()
    points.points = o3d.utility.Vector3dVector(np.asarray([np.dot(fcc_transform(), p[1:])
                                                           for p in sim.points()]))

    o3d.geometry.PointCloud(points)
    o3d.visualization.draw_geometries([points])


def run_mode(goal):
    simulation = OmniSimulation(SimpleNeighborhood(fcc_transform()), None, [0] * (3 if is_2d else 4))

    p = ProgressBar(goal, lambda: simulation.energy)

    for i in range(goal):
        p(i)

# def large_sim():
#     simulation = OmniSimulation(SimpleNeighborhood(fcc_transform()), None, (0, 0, 0, 0))
#     goal = 1_000
#
#     p = ProgressBar(goal, lambda: simulation.energy)
#
#     for i in range(goal):
#         p(i)
#         simulation.add_atom(lambda l: random.randrange(l))
#
#     plot_sim(simulation)
