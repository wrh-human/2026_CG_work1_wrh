import taichi as ti
import numpy as np
import math

# 初始化 Taichi，Mac M3 用户强制使用 Metal
ti.init(arch=ti.metal)

# --- 1. 常量与数据定义 ---
res_x, res_y = 1200, 700  # 稍微拉宽窗口，让“舞台”更大
aspect_ratio = res_x / res_y

# 三组 Field：动态插值、起始参考、结束参考
v_pos_3d_interp = ti.Vector.field(3, dtype=ti.f32, shape=8)
v_pos_2d_interp = ti.Vector.field(2, dtype=ti.f32, shape=8)

v_pos_3d_start = ti.Vector.field(3, dtype=ti.f32, shape=8)
v_pos_2d_start = ti.Vector.field(2, dtype=ti.f32, shape=8)

v_pos_3d_end = ti.Vector.field(3, dtype=ti.f32, shape=8)
v_pos_2d_end = ti.Vector.field(2, dtype=ti.f32, shape=8)

# 标准立方体顶点
cube_vertices = np.array([
    [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5],
    [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5]
], dtype=np.float32)

v_pos_3d_interp.from_numpy(cube_vertices)
v_pos_3d_start.from_numpy(cube_vertices)
v_pos_3d_end.from_numpy(cube_vertices)

indices = [0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7]

# --- 2. 变换矩阵逻辑 ---

def get_projection_matrix(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    return np.array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
        [0, 0, -1, 0]
    ], dtype=np.float32)

def get_model_matrix(angles, offset_x, offset_z):
    ax, ay, az = angles
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    
    # 复合旋转矩阵 (ZYX 顺序)
    R = np.array([
        [cy*cz, -cy*sz, sy, 0],
        [sx*sy*cz + cx*sz, -sx*sy*sz + cx*cz, -sx*cy, 0],
        [-cx*sy*cz + sx*sz, cx*sy*sz + sx*cz, cx*cy, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)
    
    T = np.eye(4, dtype=np.float32)
    T[0, 3] = offset_x
    T[2, 3] = offset_z
    return T @ R

# --- 3. Taichi 渲染内核 ---

@ti.kernel
def render_frame(mvp_i: ti.types.matrix(4, 4, ti.f32), 
                 mvp_s: ti.types.matrix(4, 4, ti.f32), 
                 mvp_e: ti.types.matrix(4, 4, ti.f32)):
    for i in range(8):
        v = ti.Vector([v_pos_3d_interp[i].x, v_pos_3d_interp[i].y, v_pos_3d_interp[i].z, 1.0])
        
        # 插值方块
        pi = mvp_i @ v
        v_pos_2d_interp[i] = ti.Vector([(pi.x/pi.w + 1.0)*0.5, (pi.y/pi.w + 1.0)*0.5])
        
        # 起始方块
        ps = mvp_s @ v
        v_pos_2d_start[i] = ti.Vector([(ps.x/ps.w + 1.0)*0.5, (ps.y/ps.w + 1.0)*0.5])

        # 结束方块
        pe = mvp_e @ v
        v_pos_2d_end[i] = ti.Vector([(pe.x/pe.w + 1.0)*0.5, (pe.y/pe.w + 1.0)*0.5])

# --- 4. 运行逻辑 (核心专业化修改) ---

gui = ti.GUI("Professional Rotation Interpolation Visualization", (res_x, res_y))

# 4.1 核心参数调整
pose_start = np.array([0.0, 0.0, 0.0])
# 增大旋转幅度：绕 X 轴两圈，Y 轴一圈，Z 轴半圈
pose_end = np.array([math.radians(720), math.radians(360), math.radians(180)])

dist_x = 2.8  # 加大左右间距，给“翻滚”留出空间
z_pos = -5.5  # 整体后退，视野更专业
speed = 0.006 # 调慢速度，让大幅度旋转更优雅

# 专业配色
COLOR_START = 0x00FFCC  # Cyan Green
COLOR_END   = 0xFF3366  # Rose Red
COLOR_INTERP = 0xFFFFFF # White

proj = get_projection_matrix(45, aspect_ratio, 0.1, 100.0)
timer = 0.0

while gui.running:
    timer += speed
    # 使用 smoothstep 函数让动画在两端更平滑
    t = (math.sin(timer - math.pi/2) + 1.0) * 0.5 
    
    # 计算当前插值状态
    curr_pose = (1.0 - t) * pose_start + t * pose_end
    curr_x = (1.0 - t) * (-dist_x) + t * dist_x
    
    # 矩阵合成
    mvp_i = proj @ get_model_matrix(curr_pose, curr_x, z_pos)
    mvp_s = proj @ get_model_matrix(pose_start, -dist_x, z_pos)
    mvp_e = proj @ get_model_matrix(pose_end, dist_x, z_pos)
    
    render_frame(mvp_i, mvp_s, mvp_e)
    
    # 渲染连线
    p_i, p_s, p_e = v_pos_2d_interp.to_numpy(), v_pos_2d_start.to_numpy(), v_pos_2d_end.to_numpy()
    for i in range(0, len(indices), 2):
        u, v = indices[i], indices[i+1]
        # 背景参考方块 (稍微细一点)
        gui.line(p_s[u], p_s[v], color=COLOR_START, radius=1)
        gui.line(p_e[u], p_e[v], color=COLOR_END, radius=1)
        # 核心动态方块 (加粗加亮)
        gui.line(p_i[u], p_i[v], color=COLOR_INTERP, radius=3)
    
    gui.text(f"Interpolation Alpha: {t:.4f}", [0.05, 0.9], font_size=20)
    gui.show()