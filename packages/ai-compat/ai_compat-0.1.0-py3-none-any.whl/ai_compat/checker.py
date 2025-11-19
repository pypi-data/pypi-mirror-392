"""Compatibility checker that evaluates system snapshot against rules."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

from .scanner import SystemSnapshot

RULE_DIR = Path(__file__).resolve().parent / "rules"


def _load_rules(filename: str) -> Dict:
    path = RULE_DIR / filename
    if not path.exists():
        return {}
    return json.loads(path.read_text())


PYTORCH_RULES = _load_rules("pytorch_rules.json")
TF_RULES = _load_rules("tensorflow_rules.json")
CUDA_RULES = _load_rules("cuda_rules.json")


@dataclass
class CompatibilityIssue:
    framework: str
    message: str
    severity: str = "warning"
    suggestion: Optional[str] = None


@dataclass
class CompatibilityReport:
    issues: List[CompatibilityIssue]
    summary: str
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            "issues": [asdict(issue) for issue in self.issues],
            "summary": self.summary,
            "metadata": self.metadata,
        }


def _version_key(version: Optional[str]) -> Optional[str]:
    if not version:
        return None
    parts = version.split(".")
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return version


def _check_cuda_driver(issues: List[CompatibilityIssue], cuda_version: Optional[str], driver_version: Optional[str]):
    if not cuda_version or not driver_version:
        return
    minimums = CUDA_RULES.get("minimum_driver", {})
    key = _version_key(cuda_version)
    required = minimums.get(key)
    if required and driver_version < required:
        issues.append(
            CompatibilityIssue(
                framework="nvidia-driver",
                severity="error",
                message=f"CUDA {cuda_version} requires driver {required}+ but system driver is {driver_version}",
                suggestion="Upgrade NVIDIA driver",
            )
        )


def _check_framework(name: str, version: Optional[str], cuda_version: Optional[str], rules: Dict[str, List[str]], issues: List[CompatibilityIssue]):
    if not version or not cuda_version:
        return
    key = _version_key(version)
    supported = rules.get(key)
    if not supported:
        issues.append(
            CompatibilityIssue(
                framework=name,
                severity="warning",
                message=f"No compatibility data for {name} {version}",
            )
        )
        return
    cuda_key = _version_key(cuda_version)
    if cuda_key not in supported:
        issues.append(
            CompatibilityIssue(
                framework=name,
                severity="error",
                message=f"{name} {version} requires CUDA {supported} but system has {cuda_version}",
                suggestion=f"Install CUDA {'/'.join(supported)} or install {name} wheel matching CUDA {cuda_version}",
            )
        )


def _check_framework_gpu(name: str, info, issues: List[CompatibilityIssue]):
    if info.version and info.gpu_available is False:
        issues.append(
            CompatibilityIssue(
                framework=name,
                severity="warning",
                message=f"{name} {info.version} is installed but GPU acceleration is not available",
                suggestion=f"Reinstall {name} with GPU build or verify drivers",
            )
        )


def check_compatibility(snapshot: SystemSnapshot) -> CompatibilityReport:
    issues: List[CompatibilityIssue] = []
    cuda_version = snapshot.gpu.cuda.version
    driver_version = snapshot.gpu.cuda.driver_version

    _check_cuda_driver(issues, cuda_version, driver_version)

    torch_info = snapshot.frameworks.get("torch")
    if torch_info:
        _check_framework("PyTorch", torch_info.version, cuda_version, PYTORCH_RULES, issues)
        _check_framework_gpu("PyTorch", torch_info, issues)

    tf_info = snapshot.frameworks.get("tensorflow")
    if tf_info:
        _check_framework("TensorFlow", tf_info.version, cuda_version, TF_RULES, issues)
        _check_framework_gpu("TensorFlow", tf_info, issues)

    onnx_info = snapshot.frameworks.get("onnxruntime")
    if onnx_info:
        _check_framework_gpu("ONNX Runtime", onnx_info, issues)

    if snapshot.gpu.gpu_count == 0:
        issues.append(
            CompatibilityIssue(
                framework="system",
                severity="error",
                message="No NVIDIA GPUs detected",
                suggestion="Install an NVIDIA GPU or verify drivers",
            )
        )

    summary = "No issues detected" if not issues else f"Detected {len(issues)} issue(s)"
    metadata = {
        "gpu_count": snapshot.gpu.gpu_count,
        "cuda_version": cuda_version,
        "driver_version": driver_version,
    }
    return CompatibilityReport(issues=issues, summary=summary, metadata=metadata)


__all__ = ["CompatibilityReport", "CompatibilityIssue", "check_compatibility"]
