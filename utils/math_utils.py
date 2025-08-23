# hematical utilities for AR operations

from OpenGL.GL import *

import cv2
import numpy as np


class MatrixUtils:
    @staticmethod
    def create_projection_matrix(
        camera_matrix: np.ndarray, shape: tuple, near: float, far: float
    ) -> np.ndarray:
        """Create OpenGL projection matrix from camera intrinsics"""

        projection_matrix = np.zeros((4, 4), np.float32)

        fx, fy = camera_matrix[0, 0], camera_matrix[1, 1]
        cx, cy = camera_matrix[0, 2], camera_matrix[1, 2]

        width, height = shape

        projection_matrix[0, 0] = 2 * fx / width
        projection_matrix[1, 1] = 2 * fy / height
        projection_matrix[2, 0] = 1 - 2 * cx / width
        projection_matrix[2, 1] = 2 * cy / height - 1
        projection_matrix[2, 2] = -(far + near) / (far - near)
        projection_matrix[2, 3] = -1.0
        projection_matrix[3, 2] = -(2 * far * near) / (far - near)

        return projection_matrix.flatten()

    @staticmethod
    def create_model_matrix(
        rvec: np.ndarray, tvec: np.ndarray, transform_matrix: np.ndarray
    ) -> np.ndarray:
        """Create model matrix from pose estimation"""

        rotation_matrix, _ = cv2.Rodrigues(rvec)
        tvec = tvec.flatten().reshape((3, 1))

        transform_matrix_4x4 = transform_matrix @ np.hstack((rotation_matrix, tvec))
        eye_matrix = np.eye(4)
        eye_matrix[:3, :] = transform_matrix_4x4

        return eye_matrix.T.flatten()
