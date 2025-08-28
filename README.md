# VR ArUco – Augmented Reality with OpenCV & OpenGL

## 📖 Introduction

`vr-aruco` is a Python-based Augmented Reality project that overlays 3D models on **ArUco markers** using **OpenCV** for computer vision and **OpenGL** for rendering.
It features a clean modular architecture, optimized performance, and real-time interactive controls for manipulating 3D objects in AR scenes.

---

## 🚀 Features

* ✅ Performance optimizations (display lists, caching, efficient NumPy ops)
* ✅ Modular and maintainable project structure
* ✅ Error handling & resource cleanup
* ✅ Interactive **model selection menu**
* ✅ Real-time **keyboard controls** for model transformation

---

## 📂 Project Structure

```
ar_project/
├── main.py                 # Entry point with interactive model selection
├── config/settings.py      # Centralized configuration
├── core/                   # Main AR functionality
│   ├── camera.py           # Camera input handling
│   ├── renderer.py         # OpenGL rendering engine
│   └── ar_engine.py        # AR pipeline and logic
├── models/                 # 3D model loading
│   ├── obj_loader.py       # Optimized OBJ file loading
│   └── material_loader.py  # MTL + texture handling
└── utils/                  # Helper utilities
    ├── math_utils.py       # Matrix and coordinate transformations
    └── exceptions.py       # Error handling
```

---

## ⚙️ Installation

### Requirements

* Python 3.8+
* OpenCV (`opencv-contrib-python`)
* PyOpenGL
* NumPy

### Setup

```bash
# Clone repository
git clone https://github.com/your-username/vr-aruco.git
cd vr-aruco

# Install dependencies
pip install -r requirements.txt

# Run project
python main.py
```

---

## 🎮 Usage

When you run the project, you will be prompted to select from available 3D models (e.g., Fox, Rocket, Solar).
The chosen model will overlay onto the detected ArUco marker in **real time**.

---

## 🎛 Controls

* `+/-` → Scale model
* `W/A/S/D` → Move along X/Y axes
* `Q/E` → Move along Z axis
* `L` → Toggle lighting
* `R` → Reset model to default
* `ESC` → Exit application

---

## 🛠 Configuration

All settings (camera parameters, projection values) are stored in:

```python
# config/settings.py

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
```

Modify these values according to your camera calibration and AR needs.

---

## 🐞 Troubleshooting

* **No camera detected** → Check `CAMERA_INDEX` in `settings.py`
* **3D model not loading** → Ensure `.obj` and `.mtl` exist in `/models`
* **Laggy performance** → Reduce resolution or use lower-poly models

---

## 📦 Requirements

Add the following to `requirements.txt`:

```txt
numpy
opencv-python
PyOpenGL
pygame
```

---

## 👨‍💻 Contributors

* **Udham Singh** – Project Author

---

## 📜 License

MIT License (or your chosen license)