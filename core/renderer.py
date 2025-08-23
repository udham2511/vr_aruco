# OpenGL rendering manager with state management


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import cv2
import numpy as np

from config.settings import ARConfig
from utils.exceptions import RenderError


class OpenGLRenderer:
    def __init__(self, window_size: tuple):
        self.window_size = window_size
        self.background_texture_id = None
        self.lighting_enabled = True
        self.is_initialized = False

    def initialize(self) -> None:
        """Initialize OpenGL settings"""

        try:
            # Basic OpenGL setup
            glClearColor(0.0, 0.0, 0.0, 1.0)
            glClearDepth(1.0)
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LEQUAL)  # Changed from GL_LESS for better depth handling
            glShadeModel(GL_SMOOTH)

            # Enable alpha blending for transparency
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Lighting setup
            self._setup_lighting()

            # Texture setup
            glEnable(GL_TEXTURE_2D)
            self.background_texture_id = glGenTextures(1)

            # Viewport setup
            glViewport(0, 0, *self.window_size)

            self.is_initialized = True
            print("OpenGL renderer initialized successfully")

        except Exception as e:
            raise RenderError(f"Failed to initialize OpenGL: {str(e)}")

    def _setup_lighting(self) -> None:
        """Configure lighting system"""

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # Set light properties
        glLightfv(GL_LIGHT0, GL_AMBIENT, ARConfig.AMBIENT_LIGHT)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, ARConfig.DIFFUSE_LIGHT)
        glLightfv(GL_LIGHT0, GL_SPECULAR, ARConfig.SPECULAR_LIGHT)
        glLightfv(GL_LIGHT0, GL_POSITION, ARConfig.LIGHT_POSITION)

        # Enable color material
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Set material properties
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

    def clear_buffers(self) -> None:
        """Clear color and depth buffers"""

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def setup_camera_view(self, projection_matrix: np.ndarray = None) -> None:
        """Setup camera view for background rendering"""

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if projection_matrix is not None:
            glMultMatrixf(projection_matrix)

        else:
            # Default perspective for background
            aspect = self.window_size[0] / self.window_size[1]
            gluPerspective(
                ARConfig.FOV, aspect, ARConfig.NEAR_PLANE, ARConfig.FAR_PLANE
            )

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def render_background(self, frame: np.ndarray) -> None:
        """Render camera frame as background with proper state management"""

        if not self.is_initialized:
            return

        # Save current OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)

        try:
            # Disable depth testing and lighting for background
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)
            glDisable(GL_BLEND)

            # Enable texturing
            glEnable(GL_TEXTURE_2D)

            # Setup orthographic projection for background
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(-1, 1, -1, 1, -1, 1)

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

            # Prepare texture
            self._update_background_texture(frame)

            # Render full-screen quad
            glColor3f(1.0, 1.0, 1.0)  # Ensure white color for proper texture display
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex2f(-1.0, -1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex2f(1.0, -1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex2f(1.0, 1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex2f(-1.0, 1.0)
            glEnd()

            # Restore matrices
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)

        except Exception as e:
            print(f"Error rendering background: {str(e)}")

        finally:
            # Restore OpenGL state
            glPopAttrib()

    def _update_background_texture(self, frame: np.ndarray) -> None:
        """Update background texture from camera frame"""

        # Convert BGR to RGB and flip vertically for OpenGL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_flipped = np.flipud(frame_rgb)

        height, width = frame_flipped.shape[:2]

        glBindTexture(GL_TEXTURE_2D, self.background_texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            width,
            height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            frame_flipped.tobytes(),
        )

    def setup_3d_view(self, projection_matrix: np.ndarray) -> None:
        """Setup 3D view for AR objects"""

        # Re-enable depth testing and lighting for 3D objects
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)

        # Setup projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(projection_matrix)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def apply_model_transform(
        self,
        model_matrix: np.ndarray,
        scale: float = 1.0,
        translation: tuple = (0, 0, 0),
    ) -> None:
        """Apply model transformation matrix"""

        glLoadMatrixf(model_matrix)

        # Apply scale and translation
        if scale != 1.0:
            glScalef(scale, scale, scale)

        if any(t != 0 for t in translation):
            glTranslatef(*translation)

    def toggle_lighting(self) -> bool:
        """Toggle lighting on/off"""

        self.lighting_enabled = not self.lighting_enabled

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
            print("Lighting enabled")

        else:
            glDisable(GL_LIGHTING)
            print("Lighting disabled")

        return self.lighting_enabled

    def swap_buffers(self) -> None:
        """Swap front and back buffers"""

        glutSwapBuffers()

    def cleanup(self) -> None:
        """Clean up OpenGL resources"""

        if self.background_texture_id:
            glDeleteTextures([self.background_texture_id])
            self.background_texture_id = None

        self.is_initialized = False
