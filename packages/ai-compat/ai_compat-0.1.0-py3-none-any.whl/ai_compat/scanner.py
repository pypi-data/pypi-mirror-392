"""High level system scanner for AI frameworks and GPU resources."""

from __future__ import annotations

import importlib
import importlib.util
import platform
from dataclasses import dataclass, asdict
from typing import Dict, Optional

from .gpu import GPUState, detect_gpu_state


@dataclass
class FrameworkInfo:
    name: str
    version: Optional[str]
    gpu_available: Optional[bool]


@dataclass
class SystemSnapshot:
    platform: str
    python_version: str
    gpu: GPUState
    frameworks: Dict[str, FrameworkInfo]


def _detect_framework(name: str, gpu_check) -> FrameworkInfo:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return FrameworkInfo(name=name, version=None, gpu_available=None)
    module = importlib.import_module(name)
    version = getattr(module, "__version__", None)
    gpu_available = None
    try:
        gpu_available = gpu_check(module)
    except Exception:
        gpu_available = None
    return FrameworkInfo(name=name, version=version, gpu_available=gpu_available)


def _torch_gpu_check(torch_module) -> bool:
    return bool(getattr(torch_module.cuda, "is_available", lambda: False)())


def _tensorflow_gpu_check(tf_module) -> bool:
    devices = getattr(tf_module.config, "list_physical_devices", lambda *_: [])("GPU")
    return bool(devices)


def _onnx_gpu_check(onnxruntime_module) -> bool:
    providers = getattr(onnxruntime_module, "get_available_providers", lambda: [])()
    return any("CUDA" in provider for provider in providers)


def _diffusers_gpu_check(diffusers_module) -> bool:
    torch = importlib.import_module("torch") if importlib.util.find_spec("torch") else None
    return bool(torch and torch.cuda.is_available())


def _transformers_gpu_check(transformers_module) -> bool:
    torch = importlib.import_module("torch") if importlib.util.find_spec("torch") else None
    return bool(torch and torch.cuda.is_available())


FRAMEWORKS = {
    "torch": _torch_gpu_check,
    "tensorflow": _tensorflow_gpu_check,
    "onnxruntime": _onnx_gpu_check,
    "diffusers": _diffusers_gpu_check,
    "transformers": _transformers_gpu_check,
}


def scan_system() -> SystemSnapshot:
    gpu_state = detect_gpu_state()
    frameworks = {
        name: _detect_framework(name, checker)
        for name, checker in FRAMEWORKS.items()
    }
    return SystemSnapshot(
        platform=f"{platform.system()} {platform.release()}",
        python_version=platform.python_version(),
        gpu=gpu_state,
        frameworks=frameworks,
    )


def snapshot_to_dict(snapshot: SystemSnapshot) -> Dict:
    data = asdict(snapshot)
    data["gpu"] = asdict(snapshot.gpu)
    data["gpu"]["gpus"] = [asdict(gpu) for gpu in snapshot.gpu.gpus]
    data["gpu"]["cuda"] = asdict(snapshot.gpu.cuda)
    data["frameworks"] = {name: asdict(info) for name, info in snapshot.frameworks.items()}
    return data


__all__ = ["scan_system", "SystemSnapshot", "snapshot_to_dict"]
