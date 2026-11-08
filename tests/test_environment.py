import json
import math

import numpy as np
import pytest
import torch

from llm_tutorial.environment import main, run_probe


def assert_success(result, device):
    assert result["actual_device"].split(":")[0] == device
    assert result["forward_finite"]
    assert result["backward_finite"]
    assert result["parameters_changed"]
    assert math.isfinite(result["loss_before"])
    assert math.isfinite(result["loss_after"])
    assert result["gradient_l1"] > 0
    assert result["update_l1"] > 0
    assert result["loss_after"] < result["loss_before"]
    assert result["output_shape"] == [8, 2]


def test_cpu_executes_forward_backward_and_update():
    result = run_probe("cpu")
    assert_success(result, "cpu")
    assert result["output_dtype"] == "torch.float32"
    assert result["gpu"] is None
    assert not result["cuda_synchronized"]


def test_numpy_torch_round_trip():
    values = np.array([1, 2, 3], dtype=np.float32)
    tensor = torch.from_numpy(values)
    np.testing.assert_array_equal((tensor + 1).numpy(), values + 1)


@pytest.mark.parametrize(
    "device,dtype",
    [("auto", "float32"), ("cpu", "float16"), ("cpu", "bfloat16")],
)
def test_unsupported_requests_are_rejected(device, dtype):
    with pytest.raises(ValueError):
        run_probe(device, dtype)


def test_unavailable_cuda_never_falls_back(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(RuntimeError, match="no CPU fallback"):
        run_probe("cuda")


def test_unsupported_bf16_never_changes_precision(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(
        torch.cuda, "is_bf16_supported", lambda **kwargs: False
    )
    with pytest.raises(RuntimeError, match="BF16 is unavailable"):
        run_probe("cuda", "bfloat16")


def test_nonfinite_forward_is_rejected(monkeypatch):
    original = torch.nn.Linear.forward
    monkeypatch.setattr(
        torch.nn.Linear, "forward", lambda self, inputs: original(self, inputs) * float("nan")
    )
    with pytest.raises(RuntimeError, match="non-finite loss"):
        run_probe("cpu")


def test_noop_optimizer_is_not_reported_as_success(monkeypatch):
    monkeypatch.setattr(torch.optim.SGD, "step", lambda self: None)
    with pytest.raises(RuntimeError, match="parameter update"):
        run_probe("cpu")


def test_cli_writes_parseable_report(tmp_path, capsys):
    path = tmp_path / "runs" / "cpu.json"
    assert main(["--device", "cpu", "--output", str(path)]) == 0
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report == json.loads(capsys.readouterr().out)
    assert report["status"] == "ok"
    assert report["environment"]["torch"] == torch.__version__
    assert report["environment"]["lock_sha256"]
    assert_success(report["result"], "cpu")


def test_cli_cuda_failure_is_structured_and_nonzero(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    path = tmp_path / "cuda-error.json"
    assert main(["--device", "cuda", "--output", str(path)]) == 1
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report == json.loads(capsys.readouterr().out)
    assert report["status"] == "error"
    assert report["request"]["device"] == "cuda"
    assert report["result"] is None
    assert "no CPU fallback" in report["error"]["message"]


def test_report_write_failure_is_nonzero(tmp_path, capsys):
    assert main(["--output", str(tmp_path)]) == 1
    output = capsys.readouterr()
    assert "Could not write report" in output.err
    assert not output.out


@pytest.mark.cuda
@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA unavailable; not GPU acceptance")
@pytest.mark.parametrize("dtype", ["float32", "bfloat16"])
def test_real_cuda(dtype):
    if dtype == "bfloat16" and not torch.cuda.is_bf16_supported(including_emulation=False):
        pytest.skip("Native BF16 unavailable; not BF16 acceptance")
    result = run_probe("cuda", dtype)
    assert_success(result, "cuda")
    assert result["cuda_synchronized"]
    assert result["gpu"]["name"]
    assert result["output_dtype"] == (
        "torch.bfloat16" if dtype == "bfloat16" else "torch.float32"
    )
