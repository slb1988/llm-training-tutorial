# L01：让计算真的发生在选定设备上

## 今天只解决一个问题

**项目自己的 Python 环境，能否在 CPU 和本机 5070 上真正完成前向、反向和参数更新？**

这不是预训练，也不判断聊天能力。后续 L02 再拆解梯度数学；本课只把运行环境变成可检查、可复现的基础。

前置：已完成 L00 review；使用 Windows x64，准备好本仓库和 uv。安装步骤统一维护在 [系统环境文档](../setup/README.md)，本课不再复制一份安装流程。

## 最少概念

| 层次 | 它证明什么 | 它不能单独证明什么 |
|---|---|---|
| NVIDIA 驱动 / nvidia-smi | 系统看得到 GPU | 当前 Python 装了 CUDA Torch |
| PyTorch wheel / CUDA runtime | 这份 Python 包含对应运行时 | 当前 GPU 能正确执行全部计算 |
| 项目 .venv | 依赖与全局 Python 隔离 | 模型真的放到了 GPU 上 |
| 实际计算探针 | 当前设备可完成这次小计算 | 大模型一定装得下或有良好质量 |

本机优先使用 Windows/5070。另一台 Windows/5090 留到性能瓶颈时；未测试它不阻塞本课，也不能声称它已通过。

## 本课文件

- `pyproject.toml`、`uv.lock`、`.python-version`：依赖与 Python 系列。
- `src/llm_tutorial/environment.py`：可读的探针与 JSON 报告入口。
- `tests/test_environment.py`：CPU、拒绝静默回退、真实 CUDA 和 CLI 结果测试。
- `docs/setup/README.md`：系统安装、验收状态、排障与迁移。

## 运行与观察

在仓库根目录、安装完成后执行：

```powershell
uv run --frozen llm-env --device cpu --output runs/environment-cpu.json
uv run --frozen llm-env --device cuda --output runs/environment-gpu.json
uv run --frozen llm-env --device cuda --dtype bfloat16 --output runs/environment-gpu-bf16.json
uv run --frozen pytest -q
```

探针的数据流：

```text
8 x 4 input -> Linear(4, 2) -> 8 x 2 output -> scalar MSE loss
                                                  |
                                                  v
                         new parameters <- SGD <- gradients
```

JSON 中应能解释：
- `actual_device`：张量实际在哪，不是根据参数猜测；
- `output_dtype`：输出实际精度；BF16 通过库的 autocast 运行，基础参数保持 FP32；
- `loss_before/loss_after`：本固定微型例子的目标值；
- `gradient_l1/update_l1`：梯度和参数变化不是零；
- `cuda_synchronized`：等待 GPU 完成，不能把“工作已提交”当作“已计算成功”。

只有所有检查完成才返回 `status: ok`。命令失败、CUDA 测试 skip 或仅看到设备型号都不算 GPU 验收。

实际安装/实测状态只看 [安装文档第 5 节](../setup/README.md#5-本机验收记录)，不在这里维护第二份结果表。

## 一个小实验

分别运行 CPU 与 CUDA FP32，比较设备字段、版本、loss 和更新量。再请求 CUDA BF16，观察 `output_dtype` 与 loss 的数值差异。

预测：设备字段必须改变；不同精度不要求位级相同，但必须有限且真实更新参数。不要从这个微小例子的启动耗时推算训练速度。

## 自检

1. 为什么系统 Python 的 CPU Torch 与项目 CUDA Torch 可以同时存在？
2. 为什么 CUDA unavailable 时不能悄悄在 CPU 跑完然后返回成功？
3. 为什么这个探针通过，仍不等于能训练任意大小的语言模型或证明 5090 已通过？

## 自主扩展入口

- `[自主阅读]`：沿安装文档阅读 uv 的 PyTorch 索引配置；检查 source、runtime、device 三层各自负责什么。
- `[自主实现]`：作为 [M04](../extensions/index.md) 的前置小实验，写独立报告对照脚本，输入两份 JSON，只比较已记录的依赖/设备/结果，不推测未测试机器。验收：能区分“结果不同”“缺字段/未验证”和“明确失败”，且不改变主线探针。
- 主线不依赖完成此练习；助手未替你实现对照器。

本课完成一个提交后暂停。下一课才是 L02 张量、自动微分和参数更新的逐步拆解。
