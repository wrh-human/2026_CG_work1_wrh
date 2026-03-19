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
