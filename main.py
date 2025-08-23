import numpy as np
import os
import sys
import traceback
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.ar_engine import AREngine
from utils.exceptions import ARException, CameraError, ModelLoadError


def load_calibration_data(calibration_path: str) -> tuple:
    """Load camera calibration data"""

    try:
        if not os.path.exists(calibration_path):
            raise FileNotFoundError(f"Calibration file not found: {calibration_path}")

        calibration = np.load(calibration_path)

        if "matrix" not in calibration or "distCoeffs" not in calibration:
            raise ValueError("Calibration file must contain 'matrix' and 'distCoeffs'")

        camera_matrix = calibration["matrix"]
        dist_coeffs = calibration["distCoeffs"]

        print(f"Loaded calibration data from: {calibration_path}")
        print(f"Camera matrix shape: {camera_matrix.shape}")
        print(f"Distortion coeffs shape: {dist_coeffs.shape}")

        return camera_matrix, dist_coeffs

    except Exception as e:
        raise ARException(f"Failed to load calibration data: {str(e)}")


def get_model_configs():
    """Get predefined model configurations"""

    return {
        "bulbasaur": {"path": r"./models/bulbasaur/bulbasaur.obj", "scale": 0.05},
        "arceus": {"path": r"./models/arceus/arceus.obj", "scale": 0.03},
        "zekrom": {"path": r"./models/zekrom/zekrom.obj", "scale": 0.10},
        "gyarados": {"path": r"./models/gyarados/gyarados.obj", "scale": 0.10},
        "dragonite": {"path": r"./models/dragonite/dragonite.obj", "scale": 0.0012},
        "magikarp": {"path": r"./models/magikarp/magikarp.obj", "scale": 0.037},
        "pokemon": {"path": r"./models/pokemon/pokemon.obj", "scale": 0.40},
        "umbreon": {"path": r"./models/umbreon/umbreon.obj", "scale": 0.018},
        "mew": {"path": r"./models/mew/mew.obj", "scale": 0.0010},
        "lunala": {"path": r"./models/lunala/lunala.obj", "scale": 6.23},
        "lapras": {"path": r"./models/lapras/lapras.obj", "scale": 0.0318},
        "golbat": {"path": r"./models/golbat/golbat.obj", "scale": 0.04},
        "rocket_orbiting_moon": {"path": r"./models/rocket_orbiting_moon/rocket_orbiting_moon.obj", "scale": 0.04},
    }


def select_model() -> tuple:
    """Interactive model selection"""

    models = get_model_configs()

    print("\nAvailable 3D Models:")
    print("-" * 40)

    for i, (name, config) in enumerate(models.items(), 1):
        status = "✓" if os.path.exists(config["path"]) else "✗"
        print(f"{i:2d}. {status} {name.capitalize():12} (scale: {config['scale']})")

    print(f"{len(models)+1:2d}. Custom model path")
    print("-" * 40)

    while True:
        try:
            choice = input(f"Select model (1-{len(models)+1}): ").strip()

            if not choice:
                continue

            choice_num = int(choice)

            if 1 <= choice_num <= len(models):
                model_name = list(models.keys())[choice_num - 1]
                config = models[model_name]

                if not os.path.exists(config["path"]):
                    print(f"Error: Model file not found: {config['path']}")
                    continue

                return config["path"], config["scale"]

            elif choice_num == len(models) + 1:
                model_path = input("Enter model path: ").strip()

                if not os.path.exists(model_path):
                    print(f"Error: Model file not found: {model_path}")
                    continue

                scale_input = input("Enter scale (default 0.03): ").strip()
                scale = float(scale_input) if scale_input else 0.03

                return model_path, scale

            else:
                print(f"Invalid choice. Please enter 1-{len(models)+1}")

        except ValueError:
            print("Invalid input. Please enter a number.")

        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)


def main():
    """Main application entry point"""

    print("=" * 50)
    print("🚀 AR Viewer - Enhanced Augmented Reality")
    print("=" * 50)

    try:
        # Load camera calibration
        calibration_path = r"./config/calibration.npz"
        camera_matrix, dist_coeffs = load_calibration_data(calibration_path)

        # Select 3D model
        model_path, model_scale = select_model()

        print(f"\nInitializing AR Engine...")
        print(f"Model: {model_path}")
        print(f"Scale: {model_scale}")

        # Create and run AR engine
        ar_engine = AREngine(
            model_path=model_path,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
            model_scale=model_scale,
        )

        # Start the application
        ar_engine.run()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

    except (ARException, CameraError, ModelLoadError) as e:
        print(f"\n❌ AR Error: {str(e)}")
        sys.exit(1)

    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")

        traceback.print_exc()
        sys.exit(1)

    finally:
        print("🧹 Cleaning up...")


if __name__ == "__main__":
    main()
