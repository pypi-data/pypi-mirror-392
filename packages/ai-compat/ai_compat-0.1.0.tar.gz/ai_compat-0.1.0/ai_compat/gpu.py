"""GPU and CUDA detection utilities."""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class GPUInfo:
    """Structured information about a GPU device."""

    name: str
    memory_total_gb: Optional[float] = None
    uuid: Optional[str] = None


@dataclass
class CUDAInfo:
    """Information about CUDA toolkits installed on the system."""

    version: Optional[str]
    installation_paths: List[str]
    cudnn_version: Optional[str]
    driver_version: Optional[str]


@dataclass
class GPUState:
    """Snapshot of GPU devices and CUDA installation."""

    gpus: List[GPUInfo]
    cuda: CUDAInfo
    gpu_count: int
    has_nvidia_smi: bool


NVIDIA_SMI_COLUMNS = [
    "index",
    "name",
    "memory.total",
    "uuid",
]


def _run_command(cmd: str) -> Optional[str]:
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _parse_nvidia_smi() -> List[GPUInfo]:
    query = ",".join(NVIDIA_SMI_COLUMNS)
    output = _run_command(f"nvidia-smi --query-gpu={query} --format=csv,noheader")
    if not output:
        return []
    gpus: List[GPUInfo] = []
    for line in output.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != len(NVIDIA_SMI_COLUMNS):
            continue
        _, name, mem, uuid = parts
        mem_gb = None
        mem_match = re.search(r"([0-9.]+)\s*MiB", mem)
        if mem_match:
            mem_gb = round(float(mem_match.group(1)) / 1024, 2)
        gpus.append(GPUInfo(name=name, memory_total_gb=mem_gb, uuid=uuid))
    return gpus


def _detect_cuda_paths() -> List[str]:
    paths = set()
    candidates = [
        "/usr/local/cuda",
        "/usr/local/cuda-12.1",
        "/usr/local/cuda-12",
        "/usr/local/cuda-11.8",
        "/opt/cuda",
        str(Path.home() / "anaconda3" / "envs"),
    ]
    env_paths = os.environ.get("CUDA_PATH")
    if env_paths:
        for path in env_paths.split(os.pathsep):
            candidates.append(path)
    if platform.system() == "Windows":
        program_files = os.environ.get("ProgramFiles", "C:/Program Files")
        candidates.append(os.path.join(program_files, "NVIDIA GPU Computing Toolkit", "CUDA"))
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            paths.add(os.path.abspath(candidate))
    return sorted(paths)


def _detect_cuda_version_from_nvidia_smi() -> Optional[str]:
    output = _run_command("nvidia-smi")
    if not output:
        return None
    match = re.search(r"CUDA Version:\s+([0-9.]+)", output)
    if match:
        return match.group(1)
    return None


def _detect_cuda_version_from_nvcc() -> Optional[str]:
    nvcc_path = shutil.which("nvcc")
    if not nvcc_path:
        return None
    output = _run_command("nvcc --version")
    if not output:
        return None
    match = re.search(r"release\s+([0-9.]+)", output)
    if match:
        return match.group(1)
    return None


def _detect_cudnn_version(cuda_paths: List[str]) -> Optional[str]:
    possible_files = []
    for path in cuda_paths:
        lib_dir = Path(path) / "lib64"
        include_dir = Path(path) / "include"
        possible_files.append(lib_dir / "libcudnn.so")
        possible_files.append(include_dir / "cudnn_version.h")
    for file in possible_files:
        if not file.exists():
            continue
        try:
            content = file.read_text(errors="ignore")
        except Exception:
            continue
        match = re.search(r"CUDNN_MAJOR\s*=\s*(\d+).*?CUDNN_MINOR\s*=\s*(\d+)", content, re.S)
        if match:
            return f"{match.group(1)}.{match.group(2)}"
    return None


def detect_cuda_info() -> CUDAInfo:
    paths = _detect_cuda_paths()
    cuda_version = _detect_cuda_version_from_nvidia_smi() or _detect_cuda_version_from_nvcc()
    cudnn_version = _detect_cudnn_version(paths)
    driver_info = detect_driver_info()
    return CUDAInfo(
        version=cuda_version,
        installation_paths=paths,
        cudnn_version=cudnn_version,
        driver_version=driver_info.get("nvidia", {}).get("driver_version") if driver_info else None,
    )


def detect_driver_info() -> Dict[str, Dict[str, Optional[str]]]:
    drivers: Dict[str, Dict[str, Optional[str]]] = {}
    # NVIDIA
    output = _run_command("nvidia-smi")
    if output:
        match = re.search(r"Driver Version:\s+([0-9.]+)", output)
        drivers["nvidia"] = {"driver_version": match.group(1) if match else None}
    # AMD (rocm-smi)
    rocm_output = _run_command("rocm-smi --showdriverversion")
    if rocm_output:
        match = re.search(r"Driver Version:\s+([0-9.]+)", rocm_output)
        drivers["amd"] = {"driver_version": match.group(1) if match else None}
    return drivers


def detect_gpu_state() -> GPUState:
    gpus = _parse_nvidia_smi()
    cuda = detect_cuda_info()
    has_nvidia = bool(gpus)
    return GPUState(
        gpus=gpus,
        cuda=cuda,
        gpu_count=len(gpus),
        has_nvidia_smi=has_nvidia,
    )


def to_json(state: GPUState) -> str:
    return json.dumps(asdict(state), indent=2)


__all__ = [
    "GPUInfo",
    "CUDAInfo",
    "GPUState",
    "detect_gpu_state",
    "detect_cuda_info",
    "detect_driver_info",
    "to_json",
]
