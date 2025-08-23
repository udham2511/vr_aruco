# Configuration settings for application

import cv2
import numpy as np


class ARConfig:
    # Display settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_TITLE = b"AR Application"

    # Camera settings
    CAMERA_INDEX = 0

    # AR settings
    MARKER_SIZE = 0.16
    ARUCO_DICT = cv2.aruco.DICT_5X5_100

    # OpenGL settings
    FOV = 37.0
    NEAR_PLANE = 0.01
    FAR_PLANE = 1000.0

    # Performance settings
    MAX_FPS = 60
    TEXTURE_CACHE_SIZE = 50

    # Lighting settings
    AMBIENT_LIGHT = (0.3, 0.3, 0.3, 1.0)
    DIFFUSE_LIGHT = (0.8, 0.8, 0.8, 1.0)
    SPECULAR_LIGHT = (0.6, 0.6, 0.6, 1.0)
    LIGHT_POSITION = (0.0, 0.0, 10.0, 1.0)

    # Coordinate transformation matrix
    COORDINATE_TRANSFORM = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
