"""
Device Detection and Management
Handles GPU/CPU detection and device selection for models
"""

import torch
import logging
from typing import Optional, Literal

logger = logging.getLogger(__name__)


class DeviceManager:
    """
    Manages device selection and provides utilities for GPU/CPU operations.

    Automatically detects available hardware and provides graceful fallback.
    """

    def __init__(self, device: Literal["auto", "cpu", "cuda"] = "auto"):
        """
        Initialize device manager.

        Args:
            device: Device preference - "auto" (detect), "cpu", or "cuda"
        """
        self.requested_device = device
        self.device = self._select_device(device)
        self.device_type = "cuda" if self.device.type == "cuda" else "cpu"

        # Log device selection
        if self.device_type == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"GPU detected and selected: {gpu_name}")
        else:
            if device == "cuda":
                logger.warning("CUDA requested but not available. Falling back to CPU.")
            else:
                logger.info("Using CPU for computations")

    def _select_device(self, device: str) -> torch.device:
        """
        Select appropriate device based on availability and preference.

        Args:
            device: Device preference

        Returns:
            torch.device object
        """
        if device == "cpu":
            return torch.device("cpu")

        if device == "cuda":
            if torch.cuda.is_available():
                return torch.device("cuda")
            else:
                logger.warning("CUDA not available, falling back to CPU")
                return torch.device("cpu")

        # Auto-detect
        if torch.cuda.is_available():
            return torch.device("cuda")
        else:
            return torch.device("cpu")

    def get_device_string(self) -> str:
        """
        Get device as string for libraries that expect string format.

        Returns:
            "cuda" or "cpu"
        """
        return self.device_type

    def get_torch_device(self) -> torch.device:
        """
        Get PyTorch device object.

        Returns:
            torch.device object
        """
        return self.device

    @staticmethod
    def is_cuda_available() -> bool:
        """
        Check if CUDA is available.

        Returns:
            True if CUDA is available, False otherwise
        """
        return torch.cuda.is_available()

    @staticmethod
    def get_gpu_info() -> Optional[dict]:
        """
        Get GPU information if available.

        Returns:
            Dictionary with GPU info or None if no GPU
        """
        if not torch.cuda.is_available():
            return None

        return {
            "name": torch.cuda.get_device_name(0),
            "memory_total": torch.cuda.get_device_properties(0).total_memory / 1e9,  # GB
            "memory_allocated": torch.cuda.memory_allocated(0) / 1e9,  # GB
            "memory_reserved": torch.cuda.memory_reserved(0) / 1e9,  # GB
        }

    def clear_cache(self):
        """Clear GPU cache if using CUDA."""
        if self.device_type == "cuda":
            torch.cuda.empty_cache()
            logger.debug("Cleared GPU cache")


def get_spacy_device() -> int:
    """
    Get device ID for spaCy (uses integer format: -1 for CPU, 0+ for GPU).

    Returns:
        -1 for CPU, 0 for first GPU
    """
    if torch.cuda.is_available():
        return 0
    return -1


def check_spacy_gpu_support() -> bool:
    """
    Check if spaCy GPU support is available (requires cupy).

    Returns:
        True if spaCy can use GPU, False otherwise
    """
    try:
        import cupy
        return torch.cuda.is_available()
    except ImportError:
        return False
