import open3d as o3d

pcd = o3d.io.read_point_cloud('record_00348.pcd')
ransac = o3d.io.read_point_cloud('RANSAC_adaptive_sampling.pcd')

o3d.visualization.draw_geometries([ransac, pcd])

