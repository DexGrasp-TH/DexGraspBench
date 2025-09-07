import os
import open3d as o3d


obj_dir = "./output/so3_wo_guide_shadow/vis_obj/sem_PillBottle_81bbf3134d1ca27a58449bd132e3a3fe/tabletop_ur10e/scale006_pose006_0"
obj_name = []
for file_name in os.listdir(obj_dir):
    if '_grasp_0.obj' in file_name:
        obj_name.append(file_name.split('_grasp_0.obj')[0])
    elif '_obj.obj' in file_name:
        obj_name.append(file_name.split('_obj.obj')[0])
        
obj_name = set(obj_name)

for name in obj_name:
    hand_mesh = o3d.io.read_triangle_mesh(os.path.join(obj_dir, f"{name}_grasp_0.obj"))
    obj_mesh = o3d.io.read_triangle_mesh(os.path.join(obj_dir, f"{name}_obj.obj"))
    o3d.visualization.draw_geometries([hand_mesh, obj_mesh])
