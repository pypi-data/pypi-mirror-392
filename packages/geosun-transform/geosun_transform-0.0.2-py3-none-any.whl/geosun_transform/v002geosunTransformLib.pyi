# v002geosunTransformLib.pyi - 自动生成的类型存根文件
# 生成时间: 2025-11-17 23:39:27

from typing import Any

# 导入语句
from typing import Union, Literal, Sequence, Optional
import numpy as np
import time

# 类定义
class Lidar2Motor_1XXG:
    def __init__(self, vectorize_threshold: int = 100) -> Any: ...
    def _rotation_matrix_x(angle: float) -> Any: ...
    def _rotation_matrix_y(angle: float) -> Any: ...
    def _rotation_matrix_z(angle: float) -> Any: ...
