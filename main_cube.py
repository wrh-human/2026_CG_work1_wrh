import taichi as ti
import numpy as np

from rotate import get_model_matrix_3d, get_view_matrix, get_projection_matrix

ti.init(arch=ti.metal)

res = 800
gui = ti.GUI("M3 Metal GPU - 3D Cube (Shifted Up)", res=res)

vertices_np = np.array([
    [-1.0, -1.0,  1.0], [ 1.0, -1.0,  1.0], [ 1.0,  1.0,  1.0], [-1.0,  1.0,  1.0], # 前面 (0-3)
    [-1.0, -1.0, -1.0], [ 1.0, -1.0, -1.0], [ 1.0,  1.0, -1.0], [-1.0,  1.0, -1.0]  # 后面 (4-7)
], dtype=np.float32)

# 12 条棱（索引对）
edge_indices = np.array([
    [0, 1], [1, 2], [2, 3], [3, 0], 
    [4, 5], [5, 6], [6, 7], [7, 4], 
    [0, 4], [1, 5], [2, 6], [3, 7]  
], dtype=np.int32)

v_pos_3d = ti.Vector.field(3, dtype=ti.f32, shape=8)
v_pos_2d = ti.Vector.field(2, dtype=ti.f32, shape=8)
v_pos_3d.from_numpy(vertices_np)

@ti.kernel
def transform_kernel(mvp: ti.types.matrix(4, 4, ti.f32)):
    for i in v_pos_3d:
        v_h = ti.Vector([v_pos_3d[i].x, v_pos_3d[i].y, v_pos_3d[i].z, 1.0])
        p = mvp @ v_h
        w_inv = 1.0 / p.w
        ndc_x = p.x * w_inv
        ndc_y = p.y * w_inv
        v_pos_2d[i] = ti.Vector([(ndc_x + 1.0) * 0.5, (ndc_y + 1.0) * 0.5])

angle = 0.0
eye_pos = np.array([0, 0, 8]) 
offset_y = 0.0

print("M3 GPU 渲染启动！按下 A/D 旋转，ESC 退出。")

while gui.running:
    if gui.is_pressed('a'): angle += 2.0
    if gui.is_pressed('d'): angle -= 2.0
    if gui.get_event(ti.GUI.PRESS) and gui.event.key == ti.GUI.ESCAPE:
        break

    model = get_model_matrix_3d(angle, offset_y=offset_y)
    view  = get_view_matrix(eye_pos)

    proj  = get_projection_matrix(40.0, 1.0, 0.1, 50.0)

    mvp_matrix = proj @ view @ model

    transform_kernel(mvp_matrix)

    gui.clear(0x050510)
    
    pts = v_pos_2d.to_numpy()

    for i in range(12):
        u, v = edge_indices[i]

        color = 0x00FFD2 if i < 4 else 0x00CCAA
        gui.line(pts[u], pts[v], color=color, radius=3)
    
    gui.circles(pts, color=0xFFFFFF, radius=5)

    gui.show()