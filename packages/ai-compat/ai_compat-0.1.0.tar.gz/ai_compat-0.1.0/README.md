# ai-compat

AI GPU compatibility toolkit that inspects, tests, and auto-fixes CUDA/driver mismatches for major AI frameworks.

## Features

- GPU + CUDA detection (`nvidia-smi`, CUDA paths, cuDNN)
- Framework scanner for PyTorch, TensorFlow, ONNX Runtime, diffusers, transformers
- Compatibility checker with JSON rules
- Auto-fix suggestions + optional pip installs
- GPU diagnostics (PyTorch/TensorFlow/ONNX/VRAM tests)
- Environment file exporter (`gpu-env.txt`)
- CLI entry point: `ai-compat`

## Quickstart

```bash
pip install ai-compat
ai-compat scan
ai-compat check
ai-compat fix --apply
ai-compat test
ai-compat export --output gpu-env.txt
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
  checker.py    # rules-based compatibility engine
  fixer.py      # auto-fix planner
  tester.py     # GPU diagnostics
  exporter.py   # environment generator
  rules/
    cuda_rules.json
    pytorch_rules.json
    tensorflow_rules.json
```

## Limitations

- Requires `nvidia-smi` for NVIDIA detection
- Auto-fix commands run via `pip`; `--apply` executes them (use with caution)
- VRAM stress test relies on PyTorch
- Rules JSON provides conservative reference mappings; update as needed

Contributions welcome!
