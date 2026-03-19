# 计算机图形学实验二：旋转与变换

本实验旨在通过Taichi Lang框架在Mac M3芯片（本人所用）上实现一个具有实时交互功能的**三角形平面旋转**以及**3D方体旋转渲染器**。实验涵盖了**坐标变换基本workflow**的核心理论与实践。ps.我在设计实验的过程中发现，所有的3D酷炫效果，本质上都是从2D平面的几何变换一步步推导出来的。

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
```


---
## 2. 核心理论：从平面到空间的跨越

### 2.1基础：2D 平面的旋转理论
在2D平面中，如果我们想让一个点 $(x, y)$ 绕原点旋转 $\theta$ 角度，其实就是初中数学里的三角函数变换。
通过旋转矩阵 $R_{2d}$，我们可以得到变换后的坐标：

$$\begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix}$$

在`main_triangle.py`中，我就是利用这个简单的逻辑让三角形在屏幕上“转”起来的。

### 2.2进阶：3D立方体的旋转与平移
到了3D空间，情况变得有趣了。一个立方体有8个顶点，我们要同时考虑$X, Y, Z$三个轴。

**我的理解：** 3D旋转其实就是一种“降维打击”。我们先让立方体绕着不同的轴旋转，然后再通过一个平移矩阵把它“提”到页面上方。

$$M = T(0, 1.2, 0) \cdot R_y(\theta) \cdot R_z(\theta)$$
* **旋转顺序很重要**：我实验发现，必须先旋转再平移。如果先平移，立方体就会像大摆锤一样绕着原点甩，而不是在原地自转。

### 2.3 终点：透视投影（为什么能看到远近？）
为了让立方体看起来“真实”，我们需要模拟人眼的“近大远小”。这就用到了透视投影矩阵 $P$。
它最核心的作用是处理 $Z$ 轴（深度）。变换公式如下：
$$V_{clip} = P \cdot V \cdot M \cdot V_{local}$$
最后通过**透视除法**（除以 $w$ 分量），原本 3D 的坐标就变成我们屏幕上看到的 2D 点了。

---

## 3. 关键代码实现 

在 `main_cube.py` 中，最让我觉得有趣的是这个 GPU 加速的内核函数，它一瞬间处理了所有顶点的数学运算：

```python
@ti.kernel
def transform_kernel(mvp: ti.types.matrix(4, 4, ti.f32)):
    for i in v_pos_3d:
        # 1. 把 3D 点包装成齐次坐标 [x, y, z, 1.0]
        v_h = ti.Vector([v_pos_3d[i].x, v_pos_3d[i].y, v_pos_3d[i].z, 1.0])
        
        # 2. 核心：一次矩阵乘法完成所有变换 (MVP)
        p = mvp @ v_h
        
        # 3. 透视除法：这是产生“远小”效果的关键
        w_inv = 1.0 / p.w  
        
        # 4. 映射到屏幕坐标系 (0~1 范围)
        v_pos_2d[i] = ti.Vector([(p.x * w_inv + 1.0) * 0.5, (p.y * w_inv + 1.0) * 0.5])
```
---

## 4. 实验结果展示 (Demos)
这是我最终跑出来的效果，立方体和三角形如愿以偿地在屏幕中上方优雅自转：
