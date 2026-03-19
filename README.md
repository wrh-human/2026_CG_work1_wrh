# 计算机图形学实验报告：3D 立方体透视投影与变换实现

本实验旨在通过 Taichi Lang 框架在 Mac M3 芯片（Metal 后端）上实现一个具有实时交互功能的 3D 立方体旋转渲染器。实验涵盖了坐标变换流水线（Transform Pipeline）的核心理论与实践。

---

## 1. 项目环境与文件结构说明

本项目代码已托管至 GitHub，采用 Git 进行版本管理。

### 1.1 文件结构 (File Structure)
```text
Work1/
├── .gitignore              # 忽略 __pycache__ 等冗余文件
├── main_cube.py            # 立方体渲染主程序 (M3 Metal 驱动)
├── main_triangle.py        # 基础三角形渲染测试
├── rotate.py               # 变换矩阵计算核心库 (Model/View/Projection)
└── videos/                 # 实验演示效果图
    ├── cube_demo.gif       # 立方体旋转平移演示
    └── triangle_demo.gif   # 基础光栅化演示
