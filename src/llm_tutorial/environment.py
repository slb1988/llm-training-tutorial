"""L01: prove that the selected runtime can compute, not just import."""

import argparse
from contextlib import nullcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

import torch


def command_output(arguments: list[str]) -> str | None:
    try:
        result = subprocess.run(
            arguments, capture_output=True, text=True, timeout=5, check=True
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def environment_info() -> dict:
    revision = command_output(["git", "rev-parse", "HEAD"])
    changes = command_output(["git", "status", "--porcelain"])
    lock = Path("uv.lock")
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "nvidia_driver_inventory": command_output(
            ["nvidia-smi", "--query-gpu=index,driver_version", "--format=csv,noheader"]
        ),
        "git_revision": revision,
        "git_dirty": None if changes is None else bool(changes),
        "lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest() if lock.exists() else None,
    }


def run_probe(device_name: str = "cpu", dtype: str = "float32") -> dict:
    if device_name not in {"cpu", "cuda"}:
        raise ValueError("device must be cpu or cuda; automatic fallback is not supported")
    if dtype not in {"float32", "bfloat16"}:
        raise ValueError("dtype must be float32 or bfloat16")
    if dtype == "bfloat16" and device_name != "cuda":
        raise ValueError("This lesson probes BF16 on CUDA; use float32 for the CPU probe")
    if device_name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable; no CPU fallback was used")
    if dtype == "bfloat16" and not torch.cuda.is_bf16_supported(including_emulation=False):
        raise RuntimeError("Native CUDA BF16 is unavailable; request float32 explicitly")

    device = torch.device(device_name)
    torch.manual_seed(0)
    model = torch.nn.Linear(4, 2).to(device)
    inputs = torch.arange(32, dtype=torch.float32, device=device).reshape(8, 4) / 32
    targets = torch.zeros(8, 2, device=device)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    before = [parameter.detach().clone() for parameter in model.parameters()]

    def precision_context():
        return (
            torch.autocast("cuda", dtype=torch.bfloat16)
            if dtype == "bfloat16"
            else nullcontext()
        )

    optimizer.zero_grad(set_to_none=True)
    with precision_context():
        predictions = model(inputs)
        loss = torch.nn.functional.mse_loss(predictions.float(), targets)
    if predictions.device != inputs.device or predictions.device.type != device_name:
        raise RuntimeError("Computation did not run on the requested device")
    if not torch.isfinite(loss).item():
        raise RuntimeError("Forward computation produced a non-finite loss")

    loss.backward()
    gradients = [parameter.grad for parameter in model.parameters()]
    if any(gradient is None for gradient in gradients):
        raise RuntimeError("Backward computation did not populate every gradient")
    if not all(torch.isfinite(gradient).all().item() for gradient in gradients):
        raise RuntimeError("Backward computation produced non-finite gradients")
    gradient_l1 = sum(gradient.abs().sum().item() for gradient in gradients)
    if not math.isfinite(gradient_l1) or gradient_l1 <= 0:
        raise RuntimeError("Backward computation did not produce a finite nonzero gradient")

    optimizer.step()
    if not all(torch.isfinite(parameter).all().item() for parameter in model.parameters()):
        raise RuntimeError("Optimizer produced non-finite parameters")
    update_l1 = sum(
        (parameter.detach() - old).abs().sum().item()
        for parameter, old in zip(model.parameters(), before)
    )
    if not math.isfinite(update_l1) or update_l1 <= 0:
        raise RuntimeError("Optimizer did not perform a finite nonzero parameter update")

    with torch.no_grad(), precision_context():
        final_loss = torch.nn.functional.mse_loss(model(inputs).float(), targets)
    if not torch.isfinite(final_loss).item():
        raise RuntimeError("Post-update computation produced a non-finite loss")

    gpu = None
    if device_name == "cuda":
        # CUDA errors can be asynchronous; acceptance includes synchronization.
        torch.cuda.synchronize(device)
        properties = torch.cuda.get_device_properties(device)
        gpu = {
            "name": properties.name,
            "total_memory_mib": round(properties.total_memory / 2**20),
            "compute_capability": f"{properties.major}.{properties.minor}",
            "compiled_architectures": torch.cuda.get_arch_list(),
            "native_bf16": torch.cuda.is_bf16_supported(including_emulation=False),
        }

    return {
        "actual_device": str(predictions.device),
        "requested_precision": dtype,
        "output_dtype": str(predictions.dtype),
        "input_shape": list(inputs.shape),
        "output_shape": list(predictions.shape),
        "seed": 0,
        "loss_before": loss.item(),
        "loss_after": final_loss.item(),
        "gradient_l1": gradient_l1,
        "update_l1": update_l1,
        "forward_finite": True,
        "backward_finite": True,
        "parameters_changed": True,
        "cuda_synchronized": device_name == "cuda",
        "gpu": gpu,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--dtype", choices=["float32", "bfloat16"], default="float32")
    parser.add_argument("--output", type=Path, help="Optional JSON report under runs/")
    args = parser.parse_args(argv)
    report = {
        "schema_version": 1,
        "status": "error",
        "request": {"device": args.device, "dtype": args.dtype},
        "environment": {},
        "result": None,
    }
    try:
        report["environment"] = environment_info()
        report["result"] = run_probe(args.device, args.dtype)
        report["status"] = "ok"
    except (RuntimeError, ValueError, OSError) as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)}

    payload = json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2)
    if args.output is not None:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload + "\n", encoding="utf-8")
        except OSError as error:
            print(f"Could not write report: {error}", file=sys.stderr)
            return 1
    print(payload)
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
