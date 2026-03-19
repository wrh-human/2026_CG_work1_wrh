import taichi as ti
import numpy as np
import math

def deg2rad(deg):
    return deg * math.pi / 180.0

def get_model_matrix_3d(angle, offset_y=0.0):
    rad = deg2rad(angle)
    c, s = math.cos(rad), math.sin(rad)

    ry = ti.Matrix([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])
    rz = ti.Matrix([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    rotation = ry @ rz
    
    translation = ti.Matrix([
        [1, 0, 0, 0],
        [0, 1, 0, offset_y],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    return translation @ rotation

def get_model_matrix(angle):
    rad = deg2rad(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    # 绕 Z 轴旋转矩阵
    return ti.Matrix([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ])

def get_view_matrix(eye_pos):
    return ti.Matrix([
        [1, 0, 0, -eye_pos[0]],
        [0, 1, 0, -eye_pos[1]],
        [0, 0, 1, -eye_pos[2]],
        [0, 0, 0, 1]
    ])

def get_projection_matrix(eye_fov, aspect_ratio, zNear, zFar):
    t = math.tan(deg2rad(eye_fov) / 2) * zNear
    r = t * aspect_ratio
    l, b = -r, -t
    n, f = -zNear, -zFar
    return ti.Matrix([
        [2*n/(r-l),    0,          (r+l)/(r-l),  0],
        [0,            2*n/(t-b),  (t+b)/(t-b),  0],
        [0,            0,          (n+f)/(n-f),  -2*n*f/(n-f)],
        [0,            0,          1,            0]
    ])