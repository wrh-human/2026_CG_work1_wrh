import taichi as ti
import numpy as np
import math
# 导入核心数学逻辑——旋转相关的矩阵
from rotate import get_model_matrix, get_view_matrix, get_projection_matrix

ti.init(arch=ti.metal) 

res = 700
gui = ti.GUI("M3 Metal GPU - Elegant Triangle", res=res)

# --- 数据准备 ---
# 实验要求的三个顶点坐标
v_data = np.array([
    [ 2.0, 0.0, -2.0], # v0
    [ 0.0, 2.0, -2.0], # v1
    [-2.0, 0.0, -2.0]  # v2
], dtype=np.float32)

# GPU 显存分配
v_pos_3d = ti.Vector.field(3, dtype=ti.f32, shape=3)
v_pos_2d = ti.Vector.field(2, dtype=ti.f32, shape=3)
v_pos_3d.from_numpy(v_data)

# --- GPU 顶点着色器 (Vertex Shader) ---
@ti.kernel
def render_pipeline(mvp: ti.types.matrix(4, 4, ti.f32)):
    for i in v_pos_3d:
        # 齐次坐标变换
        v_h = ti.Vector([v_pos_3d[i].x, v_pos_3d[i].y, v_pos_3d[i].z, 1.0])
        p = mvp @ v_h
        
        # 透视除法 (归一化到 NDC)
        w_inv = 1.0 / p.w
        ndc = ti.Vector([p.x * w_inv, p.y * w_inv])
        
        # 视口变换：从 NDC [-1, 1] 映射到屏幕 [0, 1]
        v_pos_2d[i] = (ndc + 1.0) * 0.5

# --- 运行参数 ---
angle = 0.0
eye_pos = np.array([0, 0, 5]) # 相机位置
frame = 0

print("M3 GPU 核心已就绪！")
print("控制: A/D 旋转, ESC 退出")

while gui.running:
    # 交互与逻辑更新
    if gui.is_pressed('a'): angle += 2.5
    if gui.is_pressed('d'): angle -= 2.5
    if gui.get_event(ti.GUI.PRESS) and gui.event.key == ti.GUI.ESCAPE: break
    
    frame += 1

    # 1. CPU 侧计算 MVP 矩阵
    model = get_model_matrix(angle)
    view = get_view_matrix(eye_pos)
    proj = get_projection_matrix(45.0, 1.0, 0.1, 50.0)
    mvp_matrix = proj @ view @ model

    # 2. 调用 Metal GPU 进行并行变换
    render_pipeline(mvp_matrix)

    # 3. 创新美化：呼吸感背景 (颜色随帧率微弱变化)
    bg_color = 0x111111 + int(math.sin(frame * 0.05) * 5)
    gui.clear(bg_color)

    # 4. 绘制三角形边框
    pts = v_pos_2d.to_numpy()
    edges = [(0, 1), (1, 2), (2, 0)]
    
    # 视觉创新：根据旋转角度动态改变线条颜色
    # 产生一种“霓虹发光”的效果
    color_val = ti.rgb_to_hex((0.5 + 0.5 * math.sin(angle*0.05), 
                               0.8, 
                               0.5 + 0.5 * math.cos(angle*0.05)))
    
    for start, end in edges:
        # 增加 radius 让线条更有质感
        gui.line(pts[start], pts[end], color=color_val, radius=3)
    
    # 5. 装饰：在顶点处绘制发光点
    for i in range(3):
        gui.circle(pts[i], color=0xFFFFFF, radius=5)

    gui.show()