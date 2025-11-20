"""TPU (Tensor Processing Unit) detection utilities for Cloud TPU and Edge TPU."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TPUInfo:
    """Information about a detected TPU device."""

    type: str  # "cloud" or "edge"
    name: Optional[str] = None
    zone: Optional[str] = None  # For Cloud TPU
    accelerator_type: Optional[str] = None  # e.g., "v2-8", "v3-8"
    state: Optional[str] = None  # "READY", "CREATING", etc.
    ip_address: Optional[str] = None  # TPU IP for Cloud TPU
    version: Optional[str] = None  # TPU software version


@dataclass
class TPUState:
    """Snapshot of TPU devices and configuration."""

    tpus: List[TPUInfo]
    tpu_count: int
    has_cloud_tpu: bool
    has_edge_tpu: bool
    cloud_tpu_available: bool
    edge_tpu_available: bool


def _run_command(cmd: str) -> Optional[str]:
    """Run a shell command and return output."""
    try:
        result = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, timeout=5
        )
        return result.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _detect_cloud_tpu() -> List[TPUInfo]:
    """Detect Google Cloud TPU using gcloud CLI."""
    tpus: List[TPUInfo] = []
    
    # Check if gcloud is available
    gcloud_path = _run_command("which gcloud")
    if not gcloud_path:
        return tpus
    
    # Try to list TPUs
    output = _run_command("gcloud compute tpus list --format=json")
    if not output:
        return tpus
    
    try:
        tpu_list = json.loads(output)
        for tpu_data in tpu_list:
            tpu_info = TPUInfo(
                type="cloud",
                name=tpu_data.get("name"),
                zone=tpu_data.get("zone", "").split("/")[-1] if tpu_data.get("zone") else None,
                accelerator_type=tpu_data.get("acceleratorType"),
                state=tpu_data.get("state"),
                ip_address=tpu_data.get("networkEndpoints", [{}])[0].get("ipAddress") if tpu_data.get("networkEndpoints") else None,
                version=tpu_data.get("tensorflowVersion") or tpu_data.get("runtimeVersion"),
            )
            tpus.append(tpu_info)
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    
    return tpus


def _detect_edge_tpu() -> List[TPUInfo]:
    """Detect Google Edge TPU devices."""
    tpus: List[TPUInfo] = []
    
    # Check for Edge TPU via USB (common on Coral devices)
    usb_devices = _run_command("lsusb | grep -i 'coral\\|google'")
    if usb_devices:
        # Try to get more info about Edge TPU
        tpu_info = TPUInfo(
            type="edge",
            name="Edge TPU (USB)",
            version=None,
        )
        tpus.append(tpu_info)
    
    # Check for Edge TPU via PCIe
    pcie_devices = _run_command("lspci | grep -i 'coral\\|google'")
    if pcie_devices:
        tpu_info = TPUInfo(
            type="edge",
            name="Edge TPU (PCIe)",
            version=None,
        )
        tpus.append(tpu_info)
    
    # Check for Edge TPU via /dev/apex_0 (common device path)
    if os.path.exists("/dev/apex_0"):
        tpu_info = TPUInfo(
            type="edge",
            name="Edge TPU (apex_0)",
            version=None,
        )
        tpus.append(tpu_info)
    
    # Check environment variables that might indicate TPU availability
    if os.environ.get("EDGE_TPU_PATH") or os.environ.get("TPU_NAME"):
        tpu_info = TPUInfo(
            type="edge",
            name="Edge TPU (env)",
            version=None,
        )
        tpus.append(tpu_info)
    
    return tpus


def _check_cloud_tpu_connectivity(tpu_info: TPUInfo) -> bool:
    """Check if Cloud TPU is accessible."""
    if not tpu_info.ip_address:
        return False
    
    # Try to ping the TPU IP
    result = _run_command(f"ping -c 1 -W 1 {tpu_info.ip_address}")
    return result is not None and "1 received" in result


def _check_edge_tpu_availability() -> bool:
    """Check if Edge TPU is available via pycoral or libedgetpu."""
    # Check if pycoral is installed and can detect TPU
    try:
        import importlib.util
        spec = importlib.util.find_spec("pycoral")
        if spec:
            from pycoral.utils import edgetpu
            devices = edgetpu.list_edge_tpus()
            return len(devices) > 0
    except Exception:
        pass
    
    # Check if libedgetpu is available
    result = _run_command("python3 -c 'import pycoral.utils.edgetpu; print(len(pycoral.utils.edgetpu.list_edge_tpus()))'")
    if result and result.isdigit() and int(result) > 0:
        return True
    
    return False


def detect_tpu_state() -> TPUState:
    """Detect all TPU devices (Cloud and Edge)."""
    cloud_tpus = _detect_cloud_tpu()
    edge_tpus = _detect_edge_tpu()
    
    all_tpus = cloud_tpus + edge_tpus
    
    # Check availability
    has_cloud = len(cloud_tpus) > 0
    has_edge = len(edge_tpus) > 0
    
    cloud_available = False
    if cloud_tpus:
        # Check if at least one Cloud TPU is accessible
        cloud_available = any(_check_cloud_tpu_connectivity(tpu) for tpu in cloud_tpus)
    
    edge_available = _check_edge_tpu_availability() if has_edge else False
    
    return TPUState(
        tpus=all_tpus,
        tpu_count=len(all_tpus),
        has_cloud_tpu=has_cloud,
        has_edge_tpu=has_edge,
        cloud_tpu_available=cloud_available,
        edge_tpu_available=edge_available,
    )


def to_json(state: TPUState) -> str:
    """Convert TPUState to JSON string."""
    return json.dumps(asdict(state), indent=2)


__all__ = [
    "TPUInfo",
    "TPUState",
    "detect_tpu_state",
    "to_json",
]

