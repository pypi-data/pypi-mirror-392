# ai-compat

AI GPU and TPU compatibility toolkit that inspects, tests, and auto-fixes CUDA/driver mismatches and TPU configurations for major AI frameworks.

## Features

### GPU Support
- GPU + CUDA detection (`nvidia-smi`, CUDA paths, cuDNN)
- Framework scanner for PyTorch, TensorFlow, ONNX Runtime, diffusers, transformers
- Compatibility checker with JSON rules
- Auto-fix suggestions + optional pip installs
- GPU diagnostics (PyTorch/TensorFlow/ONNX/VRAM tests)

### TPU Support
- **Cloud TPU** detection via `gcloud` CLI
- **Edge TPU** detection (USB/PCIe devices, pycoral)
- TensorFlow TPU compatibility checking
- TPU diagnostics (Cloud TPU, Edge TPU, TensorFlow TPU)
- Auto-fix suggestions for TPU setup

### General
- Environment file exporter (`gpu-env.txt` or `tpu-env.txt`)
- System resource snapshot (RAM + disk usage)
- CLI entry point: `ai-compat`
- Works with both GPU and TPU simultaneously

## Quickstart

```bash
pip install ai-compat
ai-compat scan          # Scan system for GPU and TPU
ai-compat check         # Check compatibility issues
ai-compat fix --apply   # Auto-fix issues
ai-compat test          # Run all tests (GPU + TPU)
ai-compat test --gpu-only  # Run only GPU tests
ai-compat test --tpu-only  # Run only TPU tests
ai-compat export --output env.txt
```

## Example Output

```
ai-compat check
{
  "issues": [
    {
      "framework": "PyTorch",
      "message": "PyTorch 2.2.1 requires CUDA ['12.1', '12.2'] but system has 11.8",
      "severity": "error",
      "suggestion": "Install CUDA 12.1/12.2 or install PyTorch wheel matching CUDA 11.8"
    }
  ],
  "summary": "Detected 1 issue(s)",
  "metadata": {
    "gpu_count": 1,
    "cuda_version": "11.8",
    "driver_version": "535.104"
  }
}
```

## Architecture

```
ai_compat/
  cli.py        # command-line interface
  scanner.py    # system + framework inspection
  gpu.py        # low-level GPU detection
  tpu.py        # TPU detection (Cloud + Edge)
  checker.py    # rules-based compatibility engine
  fixer.py      # auto-fix planner
  tester.py     # GPU + TPU diagnostics
  exporter.py   # environment generator
  rules/
    cuda_rules.json
    pytorch_rules.json
    tensorflow_rules.json
    tpu_rules.json
```

## TPU Detection

### Cloud TPU
- Requires `gcloud` CLI installed and configured
- Detects TPU via `gcloud compute tpus list`
- Checks connectivity and TensorFlow TPUClusterResolver access

### Edge TPU
- Detects USB/PCIe Edge TPU devices
- Checks for `/dev/apex_0` device
- Requires `pycoral` for full functionality

## Limitations

- Requires `nvidia-smi` for NVIDIA GPU detection
- Cloud TPU detection requires `gcloud` CLI
- Edge TPU detection requires `pycoral` for full functionality
- System resource snapshot uses `psutil` when available (falls back to `/proc`/sysconf)
- Auto-fix commands run via `pip`; `--apply` executes them (use with caution)
- VRAM stress test relies on PyTorch
- Rules JSON provides conservative reference mappings; update as needed

## Example: GPU + TPU Detection

```bash
$ ai-compat scan
{
  "platform": "Linux 5.15.0",
  "python_version": "3.10.12",
  "resources": {
    "ram_total_gb": 12.7,
    "ram_available_gb": 11.4,
    "disk_total_gb": 107.7,
    "disk_used_gb": 38.9,
    "disk_free_gb": 68.8
  },
  "gpu": {
    "gpu_count": 1,
    "gpus": [{"name": "NVIDIA RTX 4090", "memory_total_gb": 24.0}],
    "cuda": {"version": "12.1", "cudnn_version": "8.9"}
  },
  "tpu": {
    "tpu_count": 1,
    "has_cloud_tpu": true,
    "has_edge_tpu": false,
    "cloud_tpu_available": true,
    "tpus": [{"type": "cloud", "accelerator_type": "v2-8"}]
  },
  "frameworks": {
    "tensorflow": {
      "version": "2.16.0",
      "gpu_available": true,
      "tpu_available": true
    }
  }
}
```

Contributions welcome!
