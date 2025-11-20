"""AI GPU and TPU compatibility toolkit."""

from .scanner import scan_system
from .checker import CompatibilityReport, check_compatibility
from .fixer import suggest_fixes, apply_fix_plan
from .tester import run_gpu_tests, run_tpu_tests, run_all_tests
from .exporter import export_environment
from .gpu import detect_gpu_state, GPUState
from .tpu import detect_tpu_state, TPUState

__all__ = [
    "scan_system",
    "CompatibilityReport",
    "check_compatibility",
    "suggest_fixes",
    "apply_fix_plan",
    "run_gpu_tests",
    "run_tpu_tests",
    "run_all_tests",
    "export_environment",
    "detect_gpu_state",
    "detect_tpu_state",
    "GPUState",
    "TPUState",
]

__version__ = "0.2.0"
