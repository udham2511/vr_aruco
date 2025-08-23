# Material loading for 3D models

from OpenGL.GL import *
import os
import pygame

from typing import Dict, Any
from utils.exceptions import ModelLoadError


class MaterialLoader:
    def __init__(self):
        self.texture_cache = {}

    def load_mtl(self, filepath: str) -> Dict[str, Any]:
        """Load MTL file with caching and error handling"""

        if not os.path.exists(filepath):
            raise ModelLoadError(f"MTL file not found: {filepath}")

        materials = {}
        current_material = None
        base_path = os.path.dirname(filepath)

        try:
            with open(filepath, "r") as mtl_file:
                for line in mtl_file:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    parts = line.split()

                    if not parts:
                        continue

                    if parts[0] == "newmtl":
                        current_material = parts[1]
                        materials[current_material] = {}

                    elif current_material is None:
                        raise ModelLoadError("MTL file must start with 'newmtl'")

                    elif parts[0] in (
                        "map_Kd",
                        "map_Ka",
                        "map_Ks",
                        "map_Ns",
                        "map_d",
                        "refl",
                        "bump",
                    ):
                        texture_path = os.path.join(base_path, parts[1])

                        materials[current_material][parts[0]] = parts[1:]
                        materials[current_material]["texture_id"] = self._load_texture(
                            texture_path
                        )

                    else:
                        try:
                            materials[current_material][parts[0]] = [
                                float(x) for x in parts[1:]
                            ]

                        except ValueError:
                            materials[current_material][parts[0]] = parts[1:]

        except Exception as e:
            raise ModelLoadError(f"Error loading MTL file {filepath}: {str(e)}")

        return materials

    def _load_texture(self, texture_path: str) -> int:
        """Load texture with caching"""

        if texture_path in self.texture_cache:
            return self.texture_cache[texture_path]

        if not os.path.exists(texture_path):
            print(f"Warning: Texture file not found: {texture_path}")

            return 0

        try:
            surface = pygame.image.load(texture_path)
            image_data = pygame.image.tostring(surface, "RGBA", True)
            width, height = surface.get_size()

            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                width,
                height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                image_data,
            )

            self.texture_cache[texture_path] = texture_id
            print(f"Loaded texture: {texture_path} (ID: {texture_id})")

            return texture_id

        except Exception as e:
            print(f"Error loading texture {texture_path}: {str(e)}")

            return 0
