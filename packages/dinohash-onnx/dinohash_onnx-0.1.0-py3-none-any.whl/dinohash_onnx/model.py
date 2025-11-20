"""Module for loading ONNX models."""

import os
import onnxruntime as ort
from typing import Optional


# Global session cache
_session_cache: Optional[ort.InferenceSession] = None


def load_model(model_path: str, cache: bool = True, device: str = 'cpu') -> ort.InferenceSession:
    """
    Loads an ONNX model for inference.

    Args:
        model_path: Path to the ONNX model file
        cache: Whether to cache the loaded model (default: True)
        device: Device to run inference on ('cpu', 'cuda', or 'dml' for DirectML)

    Returns:
        ONNX Runtime inference session

    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If model loading fails
    """
    global _session_cache

    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        # Return cached session if available
        if cache and _session_cache is not None:
            return _session_cache

        print(f"Loading ONNX model from {model_path}")

        # Configure execution providers based on device
        providers = []
        if device == 'cuda':
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        elif device == 'dml':
            providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
        else:  # cpu or default
            providers = ['CPUExecutionProvider']

        # Create inference session
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        session = ort.InferenceSession(
            model_path,
            sess_options=session_options,
            providers=providers
        )

        # Cache session if requested
        if cache:
            _session_cache = session

        return session

    except Exception as error:
        print(f"Error loading ONNX model: {error}")
        raise
