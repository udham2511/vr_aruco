# Main AR engine combining all components

from OpenGL.GLUT import *
from OpenGL.GL import *

import cv2
import numpy as np

from config.settings import ARConfig
from models.obj_loader import OBJModel

from core.camera import CameraManager
from core.renderer import OpenGLRenderer

from utils.math_utils import MatrixUtils
from utils.exceptions import ARException


class AREngine:
    def __init__(
        self,
        model_path: str,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        model_scale: float = 0.03,
    ):

        # Core components
        self.camera_manager = CameraManager()
        self.renderer = None
        self.model = None

        # AR parameters
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.model_scale = model_scale
        self.model_path = model_path

        # ArUco detection
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(ARConfig.ARUCO_DICT)
        self.aruco_params = cv2.aruco.DetectorParameters()

        # Transform matrices
        self.projection_matrix = None
        self.coordinate_transform = ARConfig.COORDINATE_TRANSFORM

        # User controls
        self.translation = {"x": 0, "y": 0, "z": 0}
        self.swap_yz = True

        # State
        self.is_running = False
        self.window_id = None

    def initialize(self) -> None:
        """Initialize all AR components"""

        try:
            # Initialize camera
            self.camera_manager.initialize()
            camera_dims = self.camera_manager.get_dimensions()

            # Initialize GLUT and create window
            glutInit()
            glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_ALPHA)
            glutInitWindowSize(*camera_dims)

            self.window_id = glutCreateWindow(ARConfig.WINDOW_TITLE)

            # Initialize renderer
            self.renderer = OpenGLRenderer(camera_dims)
            self.renderer.initialize()

            # Load 3D model
            self.model = OBJModel(self.model_path, swap_yz=self.swap_yz)

            # Create projection matrix
            self.projection_matrix = MatrixUtils.create_projection_matrix(
                self.camera_matrix, camera_dims, ARConfig.NEAR_PLANE, ARConfig.FAR_PLANE
            )

            # Setup GLUT callbacks
            glutDisplayFunc(self._render_frame)
            glutIdleFunc(self._render_frame)
            glutKeyboardFunc(self._handle_keyboard)
            glutReshapeFunc(self._handle_reshape)

            print("AR Engine initialized successfully")

        except Exception as e:
            self.cleanup()

            raise ARException(f"Failed to initialize AR engine: {str(e)}")

    def _render_frame(self) -> None:
        """Main rendering loop"""

        try:
            # Get current frame
            frame = self.camera_manager.get_frame()

            if frame is None:
                return

            # Clear buffers
            self.renderer.clear_buffers()

            # Render background (camera feed)
            self.renderer.render_background(frame)

            # Detect ArUco markers and render 3D objects
            self._detect_and_render_markers(frame)

            # Swap buffers
            self.renderer.swap_buffers()

        except Exception as e:
            print(f"Render error: {str(e)}")

    def _detect_and_render_markers(self, frame: np.ndarray) -> None:
        """Detect ArUco markers and render 3D models"""

        # Convert to grayscale for marker detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )

        if ids is not None and len(ids) > 0:
            # Estimate pose for each marker
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, ARConfig.MARKER_SIZE, self.camera_matrix, self.dist_coeffs
            )

            # Setup 3D rendering
            self.renderer.setup_3d_view(self.projection_matrix)

            # Render model for each detected marker
            for i in range(len(ids)):
                self._render_model_on_marker(rvecs[i], tvecs[i])

    def _render_model_on_marker(self, rvec: np.ndarray, tvec: np.ndarray) -> None:
        """Render 3D model on detected marker"""

        try:
            # Create model transformation matrix
            model_matrix = MatrixUtils.create_model_matrix(
                rvec, tvec, self.coordinate_transform
            )

            # Apply transformations
            self.renderer.apply_model_transform(
                model_matrix,
                scale=self.model_scale,
                translation=(
                    self.translation["x"],
                    self.translation["y"],
                    self.translation["z"],
                ),
            )

            # Render the model
            self.model.render()

        except Exception as e:
            print(f"Model rendering error: {str(e)}")

    def _handle_keyboard(self, key, x: int, y: int) -> None:
        """Handle keyboard input for controls"""

        try:
            key_str = key.decode("utf-8").lower()

            # Scale controls
            if key_str == "+" or key_str == "=":
                self.model_scale *= 1.1
                print(f"Scale: {self.model_scale:.4f}")

            elif key_str == "-":
                self.model_scale *= 0.9
                print(f"Scale: {self.model_scale:.4f}")

            # Translation controls
            elif key_str == "w":
                self.translation["y"] -= 0.01
                print(f"Translation Y: {self.translation['y']:.3f}")

            elif key_str == "s":
                self.translation["y"] += 0.01
                print(f"Translation Y: {self.translation['y']:.3f}")

            elif key_str == "a":
                self.translation["x"] += 0.01
                print(f"Translation X: {self.translation['x']:.3f}")

            elif key_str == "d":
                self.translation["x"] -= 0.01
                print(f"Translation X: {self.translation['x']:.3f}")

            elif key_str == "q":
                self.translation["z"] += 0.01
                print(f"Translation Z: {self.translation['z']:.3f}")

            elif key_str == "e":
                self.translation["z"] -= 0.01
                print(f"Translation Z: {self.translation['z']:.3f}")

            # Lighting toggle
            elif key_str == "l":
                self.renderer.toggle_lighting()

            # Reset controls
            elif key_str == "r":
                self.translation = {"x": 0, "y": 0, "z": 0}
                self.model_scale = 0.03

                print("Reset to defaults")

            # Quit
            elif key_str == "\x1b":  # Escape key
                self.stop()

        except Exception as e:
            print(f"Keyboard handling error: {str(e)}")

    def _handle_reshape(self, width: int, height: int) -> None:
        """Handle window reshape"""

        glViewport(0, 0, width, height)

        # Update projection matrix with new aspect ratio
        self.projection_matrix = MatrixUtils.create_projection_matrix(
            self.camera_matrix, (width, height), ARConfig.NEAR_PLANE, ARConfig.FAR_PLANE
        )

    def run(self) -> None:
        """Start the AR application main loop"""

        if not self.is_running:
            self.initialize()
            self.is_running = True

            print("AR Engine started. Controls:")
            print("  +/- : Scale model")
            print("  WASD: Move model (XY)")
            print("  Q/E : Move model (Z)")
            print("  L   : Toggle lighting")
            print("  R   : Reset to defaults")
            print("  ESC : Quit")

            glutMainLoop()

    def stop(self) -> None:
        """Stop the AR application"""

        self.is_running = False
        self.cleanup()

        glutLeaveMainLoop()

    def cleanup(self) -> None:
        """Clean up all resources"""
        try:
            if self.model:
                self.model.cleanup()
                self.model = None

            if self.renderer:
                self.renderer.cleanup()
                self.renderer = None

            if self.camera_manager:
                self.camera_manager.release()

            if self.window_id:
                glutDestroyWindow(self.window_id)
                self.window_id = None

            print("AR Engine cleanup completed")

        except Exception as e:
            print(f"Cleanup error: {str(e)}")
