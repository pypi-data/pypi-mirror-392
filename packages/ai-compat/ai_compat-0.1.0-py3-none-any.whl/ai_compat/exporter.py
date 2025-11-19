"""Environment exporter."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .scanner import SystemSnapshot

DEFAULTS = {
    "python": "3.10",
    "cuda": "12.1",
    "pytorch": "2.2.0",
    "tensorflow": "2.16.0",
    "onnxruntime": "1.18.0",
}


def export_environment(snapshot: Optional[SystemSnapshot], path: Path) -> Path:
    path = Path(path)
    cuda_version = snapshot.gpu.cuda.version if snapshot else DEFAULTS["cuda"]
    python_version = snapshot.python_version if snapshot else DEFAULTS["python"]
    torch_version = snapshot.frameworks.get("torch").version if snapshot and snapshot.frameworks.get("torch") else DEFAULTS["pytorch"]
    tf_version = snapshot.frameworks.get("tensorflow").version if snapshot and snapshot.frameworks.get("tensorflow") else DEFAULTS["tensorflow"]

    content = [
        f"python={python_version}",
        f"cuda={cuda_version}",
        f"pytorch={torch_version}",
        f"tensorflow={tf_version}",
        f"onnxruntime-gpu={DEFAULTS['onnxruntime']}",
    ]
    path.write_text("\n".join(content) + "\n")
    return path


__all__ = ["export_environment"]
