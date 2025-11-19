# v003geosunTransformLib.pyi - 自动生成的类型存根文件
# 生成时间: 2025-11-18 11:03:20

from typing import Any

# 导入语句
from geosun_base import standard_euler_to_rotation_matrix
from pathlib import Path
from typing import Union, Literal, Sequence, Optional, Dict
import numpy as np
import sys
import time

# 类定义
class Lidar2Motor_1XXG:
    def __init__(self, vectorize_threshold: int = 100) -> Any: ...
    def calculate_point_differences(points1: np.ndarray, points2: np.ndarray) -> Any: ...
    def compute_statistics(data: np.ndarray) -> Any: ...
    def calculate_euclidean_distances(diff_x: np.ndarray, diff_y: np.ndarray, diff_z: np.ndarray) -> Any: ...
