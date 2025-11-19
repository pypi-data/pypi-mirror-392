"""GPU diagnostic tests."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import Callable, List


@dataclass
class TestResult:
    name: str
    success: bool
    message: str


def _run_test(name: str, func: Callable[[], str]) -> TestResult:
    try:
        message = func()
        return TestResult(name=name, success=True, message=message)
    except Exception as exc:
        return TestResult(name=name, success=False, message=str(exc))


def _torch_test() -> str:
    spec = importlib.util.find_spec("torch")
    if spec is None:
        raise RuntimeError("PyTorch not installed")
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("torch.cuda.is_available() returned False")
    torch.randn(1000, 1000, device="cuda")
    return "PyTorch can allocate tensors on GPU"


def _tf_test() -> str:
    spec = importlib.util.find_spec("tensorflow")
    if spec is None:
        raise RuntimeError("TensorFlow not installed")
    import tensorflow as tf

    gpus = tf.config.list_physical_devices("GPU")
    if not gpus:
        raise RuntimeError("TensorFlow does not see any GPUs")
    return f"TensorFlow detected {len(gpus)} GPU(s)"


def _onnx_test() -> str:
    spec = importlib.util.find_spec("onnxruntime")
    if spec is None:
        raise RuntimeError("onnxruntime not installed")
    import onnxruntime as ort

    providers = ort.get_available_providers()
    if not any("CUDA" in provider for provider in providers):
        raise RuntimeError("ONNX Runtime CUDA provider unavailable")
    return f"ONNX Runtime providers: {providers}"


def _vram_test() -> str:
    spec = importlib.util.find_spec("torch")
    if spec is None:
        raise RuntimeError("PyTorch required for VRAM test")
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA not available for VRAM test")

    sizes_gb = [1, 2, 4]
    device = torch.device("cuda")
    for size in sizes_gb:
        try:
            elements = int(size * (1024 ** 3) / 4)  # float32
            tensor = torch.empty(elements, dtype=torch.float32, device=device)
            del tensor
        except RuntimeError as exc:
            raise RuntimeError(f"Failed to allocate {size}GB on GPU: {exc}")
    return "VRAM stress test passed"


def run_gpu_tests() -> List[TestResult]:
    tests = [
        ("PyTorch GPU", _torch_test),
        ("TensorFlow GPU", _tf_test),
        ("ONNX Runtime GPU", _onnx_test),
        ("VRAM Stress", _vram_test),
    ]
    results = [_run_test(name, func) for name, func in tests]
    return results


__all__ = ["run_gpu_tests", "TestResult"]
