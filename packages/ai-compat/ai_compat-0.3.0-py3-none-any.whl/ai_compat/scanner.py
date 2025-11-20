"""High level system scanner for AI frameworks and GPU resources."""

from __future__ import annotations

import importlib
import importlib.util
import os
import platform
import shutil
from dataclasses import dataclass, asdict
from typing import Dict, Optional

from .gpu import GPUState, detect_gpu_state
from .tpu import TPUState, detect_tpu_state


@dataclass
class FrameworkInfo:
    name: str
    version: Optional[str]
    gpu_available: Optional[bool]
    tpu_available: Optional[bool] = None


@dataclass
class SystemSnapshot:
    platform: str
    python_version: str
    gpu: GPUState
    tpu: TPUState
    resources: "SystemResources"
    frameworks: Dict[str, FrameworkInfo]


@dataclass
class SystemResources:
    """System resource metrics for RAM and disk."""

    ram_total_gb: Optional[float]
    ram_available_gb: Optional[float]
    disk_total_gb: Optional[float]
    disk_used_gb: Optional[float]
    disk_free_gb: Optional[float]


def _detect_framework(name: str, gpu_check, tpu_check=None) -> FrameworkInfo:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return FrameworkInfo(name=name, version=None, gpu_available=None, tpu_available=None)
    module = importlib.import_module(name)
    version = getattr(module, "__version__", None)
    gpu_available = None
    tpu_available = None
    try:
        gpu_available = gpu_check(module)
    except Exception:
        gpu_available = None
    if tpu_check:
        try:
            tpu_available = tpu_check(module)
        except Exception:
            tpu_available = None
    return FrameworkInfo(name=name, version=version, gpu_available=gpu_available, tpu_available=tpu_available)


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


def _tensorflow_tpu_check(tf_module) -> bool:
    """Check if TensorFlow can access TPU."""
    try:
        # Check for Cloud TPU
        resolver = getattr(tf_module.distribute.cluster_resolver, "TPUClusterResolver", None)
        if resolver:
            tpu_resolver = resolver()
            tpu_address = tpu_resolver.get_master()
            if tpu_address:
                return True
    except Exception:
        pass
    
    # Check for Edge TPU
    try:
        devices = getattr(tf_module.config, "list_physical_devices", lambda *_: [])("TPU")
        return bool(devices)
    except Exception:
        pass
    
    return False


FRAMEWORKS = {
    "torch": (_torch_gpu_check, None),
    "tensorflow": (_tensorflow_gpu_check, _tensorflow_tpu_check),
    "onnxruntime": (_onnx_gpu_check, None),
    "diffusers": (_diffusers_gpu_check, None),
    "transformers": (_transformers_gpu_check, None),
}


def _bytes_to_gb(value: Optional[int]) -> Optional[float]:
    if value is None:
        return None
    try:
        return round(value / (1024 ** 3), 2)
    except Exception:
        return None


def _detect_system_resources() -> SystemResources:
    """Detect system RAM and disk usage."""

    ram_total = None
    ram_available = None
    try:
        import psutil  # type: ignore
    except ImportError:
        if hasattr(os, "sysconf"):
            try:
                page_size = os.sysconf("SC_PAGE_SIZE")
                phys_pages = os.sysconf("SC_PHYS_PAGES")
                avail_pages = os.sysconf("SC_AVPHYS_PAGES")
                if all(isinstance(val, int) for val in (page_size, phys_pages, avail_pages)):
                    ram_total = page_size * phys_pages
                    ram_available = page_size * avail_pages
            except (ValueError, OSError, AttributeError):
                pass
    else:
        try:
            vm = psutil.virtual_memory()
            ram_total = getattr(vm, "total", None)
            ram_available = getattr(vm, "available", None)
        except Exception:
            pass

    disk_total = disk_used = disk_free = None
    try:
        usage = shutil.disk_usage(os.path.abspath(os.sep))
        disk_total, disk_used, disk_free = usage.total, usage.used, usage.free
    except (FileNotFoundError, PermissionError, OSError):
        pass

    return SystemResources(
        ram_total_gb=_bytes_to_gb(ram_total),
        ram_available_gb=_bytes_to_gb(ram_available),
        disk_total_gb=_bytes_to_gb(disk_total),
        disk_used_gb=_bytes_to_gb(disk_used),
        disk_free_gb=_bytes_to_gb(disk_free),
    )


def scan_system() -> SystemSnapshot:
    gpu_state = detect_gpu_state()
    tpu_state = detect_tpu_state()
    resources = _detect_system_resources()
    frameworks = {
        name: _detect_framework(name, gpu_checker, tpu_checker)
        for name, (gpu_checker, tpu_checker) in FRAMEWORKS.items()
    }
    return SystemSnapshot(
        platform=f"{platform.system()} {platform.release()}",
        python_version=platform.python_version(),
        gpu=gpu_state,
        tpu=tpu_state,
        resources=resources,
        frameworks=frameworks,
    )


def snapshot_to_dict(snapshot: SystemSnapshot) -> Dict:
    data = asdict(snapshot)
    data["gpu"] = asdict(snapshot.gpu)
    data["gpu"]["gpus"] = [asdict(gpu) for gpu in snapshot.gpu.gpus]
    data["gpu"]["cuda"] = asdict(snapshot.gpu.cuda)
    data["tpu"] = asdict(snapshot.tpu)
    data["tpu"]["tpus"] = [asdict(tpu) for tpu in snapshot.tpu.tpus]
    data["frameworks"] = {name: asdict(info) for name, info in snapshot.frameworks.items()}
    data["resources"] = asdict(snapshot.resources)
    return data


__all__ = ["scan_system", "SystemSnapshot", "SystemResources", "snapshot_to_dict"]
