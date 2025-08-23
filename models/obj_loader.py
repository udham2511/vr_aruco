# Optimized OBJ file loader

from OpenGL.GL import *

from typing import List, Optional
import os
import numpy as np

from models.material_loader import MaterialLoader
from utils.exceptions import ModelLoadError


class OBJModel:
    def __init__(self, filepath: str, swap_yz: bool = False):
        self.filepath = filepath
        self.swap_yz = swap_yz

        # Model data
        self.vertices = []
        self.normals = []
        self.tex_coords = []
        self.faces = []
        self.materials = {}

        # OpenGL resources
        self.display_list = None
        self.material_loader = MaterialLoader()

        self._load_model()
        self._create_display_list()

    def _load_model(self) -> None:
        """Load OBJ file with error handling"""

        if not os.path.exists(self.filepath):
            raise ModelLoadError(f"OBJ file not found: {self.filepath}")

        current_material = None
        base_path = os.path.dirname(self.filepath)

        try:
            with open(self.filepath, "r") as obj_file:
                for line in obj_file:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    parts = line.split()

                    if not parts:
                        continue

                    if parts[0] == "v":
                        vertex = [float(x) for x in parts[1:4]]

                        if self.swap_yz:
                            vertex = [vertex[0], vertex[2], vertex[1]]

                        self.vertices.append(vertex)

                    elif parts[0] == "vn":
                        normal = [float(x) for x in parts[1:4]]

                        if self.swap_yz:
                            normal = [normal[0], normal[2], normal[1]]

                        self.normals.append(normal)

                    elif parts[0] == "vt":
                        self.tex_coords.append([float(x) for x in parts[1:3]])

                    elif parts[0] in ("usemtl", "usemat"):
                        current_material = parts[1]

                    elif parts[0] == "mtllib":
                        mtl_path = os.path.join(base_path, parts[1])

                        self.materials = self.material_loader.load_mtl(mtl_path)

                    elif parts[0] == "f":
                        face_data = self._parse_face(parts[1:], current_material)

                        self.faces.append(face_data)

        except Exception as e:
            raise ModelLoadError(f"Error loading OBJ file {self.filepath}: {str(e)}")

        # Convert to numpy arrays for better performance
        self.vertices = np.array(self.vertices, dtype=np.float32)

        if self.normals:
            self.normals = np.array(self.normals, dtype=np.float32)

        print(f"Loaded model: {len(self.vertices)} vertices, {len(self.faces)} faces")

    def _parse_face(self, face_parts: List[str], material: Optional[str]) -> dict:
        """Parse face definition"""

        vertices, normals, tex_coords = [], [], []

        for part in face_parts:
            indices = part.split("/")

            # Vertex index (required)
            vertices.append(int(indices[0]) - 1)  # Convert to 0-based

            # Texture coordinate index (optional)
            if len(indices) > 1 and indices[1]:
                tex_coords.append(int(indices[1]) - 1)

            else:
                tex_coords.append(-1)

            # Normal index (optional)
            if len(indices) > 2 and indices[2]:
                normals.append(int(indices[2]) - 1)

            else:
                normals.append(-1)

        return {
            "vertices": vertices,
            "normals": normals,
            "tex_coords": tex_coords,
            "material": material,
        }

    def _create_display_list(self) -> None:
        """Create optimized OpenGL display list"""

        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)

        glFrontFace(GL_CCW)

        for face in self.faces:
            self._render_face(face)

        glEndList()

    def _render_face(self, face: dict) -> None:
        """Render a single face with material"""

        material = face["material"]

        # Apply material
        if material and material in self.materials:
            self._apply_material(self.materials[material])

        else:
            # Default material
            glDisable(GL_TEXTURE_2D)
            glColor3f(0.8, 0.8, 0.8)

        # Render face
        glBegin(GL_POLYGON)
        for i in range(len(face["vertices"])):
            v_idx = face["vertices"][i]
            n_idx = face["normals"][i]
            t_idx = face["tex_coords"][i]

            # Normal
            if n_idx >= 0 and n_idx < len(self.normals):
                glNormal3fv(self.normals[n_idx])

            # Texture coordinate
            if t_idx >= 0 and t_idx < len(self.tex_coords):
                glTexCoord2fv(self.tex_coords[t_idx])

            # Vertex
            if v_idx >= 0 and v_idx < len(self.vertices):
                glVertex3fv(self.vertices[v_idx])

        glEnd()

    def _apply_material(self, material: dict) -> None:
        """Apply material properties"""

        if "texture_id" in material and material["texture_id"] > 0:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, material["texture_id"])

        else:
            glDisable(GL_TEXTURE_2D)

        # Apply color properties
        if "Kd" in material:  # Diffuse color
            color = material["Kd"][:3] if len(material["Kd"]) >= 3 else [0.8, 0.8, 0.8]
            glColor3f(*color)

    def render(self) -> None:
        """Render the model using display list"""

        if self.display_list:
            glCallList(self.display_list)

    def cleanup(self) -> None:
        """Clean up OpenGL resources"""

        if self.display_list:
            glDeleteLists(self.display_list, 1)
            self.display_list = None
