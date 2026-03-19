# 计算机图形学实验二：旋转与变换

本实验旨在通过Taichi Lang框架在Mac M3芯片（本人所用）上实现一个具有实时交互功能的**三角形平面旋转**以及**3D方体旋转渲染器**。实验涵盖了**坐标变换基本workflow**的核心理论与实践。

---

## 1. 项目环境与文件结构说明

本项目代码已托管至 GitHub，采用 Git 进行版本管理。

### 1.1 文件结构 (File Structure)
```text
Work1/
├── .gitignore              # 忽略 __pycache__ 等冗余文件
├── main_cube.py            # 完成选做任务：3D立方体渲染的main函数
├── main_triangle.py        # 完成基础任务：平面三角形旋转的main函数
├── rotate.py               # 涵盖绕z轴旋转等效果的变换矩阵计算函数
└── videos/                 # 实验演示效果图
    ├── cube_demo.gif       # 立方体demo
    └── triangle_demo.gif   # 三角形demo

## 2. 变换理论分析 (Theoretical Analysis)
渲染 3D 立方体的核心在于将 3D 空间的顶点坐标 $P_{local}$ 映射到 2D 屏幕像素点 $P_{screen}$。该过程遵循标准的 **MVP 变换流**。

### 2.1 模型变换 (Model Transformation)
为了实现立方体在自转的同时整体上移，模型矩阵 $M$ 由旋转矩阵 $R$ 与平移矩阵 $T$ 复合而成：
$$M = T(0, \text{offset}_y, 0) \cdot R_y(\theta) \cdot R_z(\theta)$$
其中，为了让立方体在屏幕上方显示，我们设置了 $\text{offset}_y = 1.2$。

### 2.2 视图变换 (View Transformation)
相机位置定义为 $E = [0, 0, 8]$，视角正对原点。视图矩阵 $V$ 将世界坐标系转换为观察者坐标系：
$$V = \begin{bmatrix} 1 & 0 & 0 & -E_x \\ 0 & 1 & 0 & -E_y \\ 0 & 0 & 1 & -E_z \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

### 2.3 透视投影 (Perspective Projection)
为了模拟人眼的“近大远小”视觉效果，我们使用了透视投影矩阵 $P$。给定垂直视野 $fov$、宽高比 $aspect$、近平面 $n$ 和远平面 $f$：
$$P = \begin{bmatrix} \frac{1}{\tan(fov/2) \cdot aspect} & 0 & 0 & 0 \\ 0 & \frac{1}{\tan(fov/2)} & 0 & 0 \\ 0 & 0 & \frac{n+f}{n-f} & \frac{2nf}{n-f} \\ 0 & 0 & 1 & 0 \end{bmatrix}$$

最终顶点的齐次坐标变换公式为：
$$V_{clip} = P \cdot V \cdot M \cdot V_{local}$$

---

## 3. 核心算法实现
### 3.1 坐标变换内核 (Taichi Kernel)
我们在 GPU 上并行处理顶点变换，通过透视除法将 4D 齐次坐标转为 2D 屏幕坐标：

```python
@ti.kernel
def transform_kernel(mvp: ti.types.matrix(4, 4, ti.f32)):
    for i in v_pos_3d:
        v_h = ti.Vector([v_pos_3d[i].x, v_pos_3d[i].y, v_pos_3d[i].z, 1.0])
        p = mvp @ v_h
        w_inv = 1.0 / p.w  # 透视除法
        # 将 NDC 映射到屏幕视口 [0, 1]
        v_pos_2d[i] = ti.Vector([(p.x * w_inv + 1.0) * 0.5, (p.y * w_inv + 1.0) * 0.5])
