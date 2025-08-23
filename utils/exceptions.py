# Custom exceptions for AR application


class ARException(Exception):
    """Base exception for AR application"""

    pass


class ModelLoadError(ARException):
    """Raised when model loading fails"""

    pass


class CameraError(ARException):
    """Raised when camera operations fail"""

    pass


class RenderError(ARException):
    """Raised when rendering operations fail"""

    pass
