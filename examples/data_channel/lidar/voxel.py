import open3d as o3d
import numpy as np

# Creëer dummy voxel data
voxel_data = np.random.rand(100, 3) * 10  # willekeurige punten in een 10x10x10-ruimte

# Zet de punten om in een voxelgrid
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(voxel_data)

voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=0.5)

# Realtime visualisatie
o3d.visualization.draw_geometries([voxel_grid])
