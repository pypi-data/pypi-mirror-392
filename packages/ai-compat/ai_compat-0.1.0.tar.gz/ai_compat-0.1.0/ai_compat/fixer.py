"""Auto-fix suggestions for GPU compatibility issues."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List

from .checker import CompatibilityIssue, CompatibilityReport


@dataclass
class FixAction:
    description: str
    command: List[str]


@dataclass
class FixPlan:
    issue: CompatibilityIssue
    actions: List[FixAction]


def suggest_fixes(report: CompatibilityReport) -> List[FixPlan]:
    plans: List[FixPlan] = []
    for issue in report.issues:
        actions: List[FixAction] = []
        if "PyTorch" in issue.framework and "requires CUDA" in issue.message:
            cuda_hint = issue.message.split("CUDA")[-1].strip()
            actions.append(
                FixAction(
                    description="Install matching PyTorch wheel",
                    command=[
                        "python",
                        "-m",
                        "pip",
                        "install",
                        f"torch==2.0.1+cu118",
                        "--extra-index-url",
                        "https://download.pytorch.org/whl/cu118",
                    ],
                )
            )
        if issue.framework == "TensorFlow" and "requires CUDA" in issue.message:
            actions.append(
                FixAction(
                    description="Install TensorFlow GPU build",
                    command=["python", "-m", "pip", "install", "tensorflow==2.15.0"],
                )
            )
        if issue.framework == "nvidia-driver":
            actions.append(
                FixAction(
                    description="Update NVIDIA driver",
                    command=["sudo", "apt", "install", "nvidia-driver-535"],
                )
            )
        if issue.framework == "system" and "No NVIDIA GPUs" in issue.message:
            actions.append(
                FixAction(
                    description="Verify hardware or use cloud GPU instance",
                    command=[],
                )
            )
        if actions:
            plans.append(FixPlan(issue=issue, actions=actions))
    return plans


def apply_fix_plan(plan: FixPlan, dry_run: bool = True) -> None:
    for action in plan.actions:
        if not action.command:
            continue
        if dry_run:
            print(f"[DRY RUN] {action.description}: {' '.join(action.command)}")
        else:
            subprocess.check_call(action.command)


__all__ = ["FixPlan", "FixAction", "suggest_fixes", "apply_fix_plan"]
