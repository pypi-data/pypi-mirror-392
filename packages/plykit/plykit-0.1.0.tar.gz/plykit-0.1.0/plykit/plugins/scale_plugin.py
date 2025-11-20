from plugin_base import BasePlugin
import open3d as o3d
import numpy as np


class ScalePlugin(BasePlugin):
    name = "点云缩放"
    description = "以几何中心为基准缩放点云"
    default_params = {"scale": 1.0}

    def run(self, input_obj, params: dict, logger):
        if isinstance(input_obj, str):
            pcd = o3d.io.read_point_cloud(input_obj)
        else:
            pcd = input_obj

        scale = float(params.get("scale", 1.0))
        points = np.asarray(pcd.points)
        center = np.mean(points, axis=0)
        scaled_points = (points - center) * scale + center

        scaled_pcd = o3d.geometry.PointCloud()
        scaled_pcd.points = o3d.utility.Vector3dVector(scaled_points)
        if pcd.has_colors():
            scaled_pcd.colors = pcd.colors

        logger(f"✅ 点云缩放完成，比例: {scale}")
        return {"updated_pcd": scaled_pcd}


def get_plugin():
    return ScalePlugin()
