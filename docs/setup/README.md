# Windows 环境安装：5070 优先，5090 按需迁移

当前选择 **Windows 原生 x64 + Python 3.11 + uv**。优先在本机 RTX 5070 开发、验证和训练；性能不足时再由用户在另一台 Windows/5090 操作。

**验证状态：L01 已在本机 Windows/5070 完成安装与实测，CPU FP32、CUDA FP32、CUDA BF16 及 13 项测试通过。** 另一台 5090 尚未测试。

## 1. 固定组合与机器边界

| 项目 | 本课选择或已观察事实 |
|---|---|
| 本机 OS | Windows 11 专业版 x64，build 26100 |
| 本机 GPU / 驱动 | RTX 5070，12227 MiB，591.59 |
| Python | 3.11 系列；本机已有 3.11.8，使用它创建隔离环境 |
| uv | 本机 0.8.4 |
| PyTorch | 2.10.0+cu128，官方 CUDA 12.8 wheel |
| 测试 / 包构建 | pytest 8.4.2 / hatchling 1.27.0 |
| 5090 | 用户确认是 Windows；具体版本、显存、驱动与执行结果待迁移时核实 |

直接依赖在 `pyproject.toml`，解析后的运行/测试依赖在 `uv.lock`。torch 只从绑定的官方 CUDA 索引获取，其余包来自 PyPI。当前锁定 Windows x64 / Python 3.11，不宣称支持其他平台。

GPU wheel 约 **2.7 GiB**，下载及解包需要额外磁盘空间。它是运行库，不是模型权重；本课没有语料下载。

## 2. 准备工具

在 PowerShell 中检查：

```powershell
git --version
uv --version
python --version
nvidia-smi
```

本机已有工具，无需重装。另一台机器若缺少工具，可由用户按需运行或使用官方安装器：

```powershell
winget install --exact --id Git.Git
winget install --exact --id astral-sh.uv
uv python install 3.11
```

安装工具后可能需要重新打开终端。上面是新机器准备路径，**本次没有运行 winget、修改全局 Python 或更新驱动**。不要为了本课自动安装 WSL、Visual Studio 或完整 CUDA Toolkit。

预编译 wheel 自带所需 CUDA 用户态组件，但仍需要兼容的 NVIDIA 驱动。只有未来确实需要构建自定义 CUDA 扩展时才另行评估 Toolkit。

## 3. 从项目锁文件建立环境

先取得**包含本课提交**的 checkout，再在仓库根目录运行。若远端还没有本课提交，由用户决定同步方式；本工具不会自动 push。不要从另一台电脑复制 `.venv`。

```powershell
uv sync --frozen --python 3.11
```

- 创建/同步项目 `.venv`，安装项目及 dev 测试依赖。
- `--frozen` 复用现有锁文件，不临时选择一套新版本。
- 以后使用 `uv run --frozen ...`，不需要激活环境或调整 PowerShell 执行策略。
- 不另跑全局 `pip install torch`；系统解释器里的旧 CPU Torch 不等于项目环境。
- 若 CUDA wheel 下载很慢，允许该命令完成。工具调用超时不代表包不兼容；重新运行可能需要重新下载，不承诺断点续传。不要反复清空缓存、换成 CPU wheel 或关闭证书校验。

## 4. 验证 CPU、GPU 与 BF16

```powershell
uv run --frozen llm-env --device cpu --output runs/environment-cpu.json
uv run --frozen llm-env --device cuda --output runs/environment-gpu.json
uv run --frozen llm-env --device cuda --dtype bfloat16 --output runs/environment-gpu-bf16.json
uv run --frozen pytest -q
```

每个探针只在一个很小的 Linear 模块上做一次 forward/backward/update，再同步 GPU；不是训练语言模型。

成功必须同时看到：
- JSON 顶层 `status: "ok"`，进程退出码为 0；
- `result.actual_device` 是实际请求的 cpu 或 cuda 设备；
- loss 与梯度有限，`gradient_l1 > 0`、`update_l1 > 0`；
- `parameters_changed: true`；GPU 还须 `cuda_synchronized: true`；
- BF16 请求得到 `output_dtype: "torch.bfloat16"`，而非静默改成其他精度。

请求 CUDA 不可用、非有限结果、优化器未更新等会返回结构化错误和非零退出码，不退回 CPU。此课 BF16 探针仅面向支持原生 BF16 的 CUDA；CPU 使用 FP32。

测试中的 CUDA 用例在没有 GPU 时会标记 skip；**skip 不能代替 GPU 验收**，必须单独看 CUDA 探针。可以仅运行 CPU/错误路径测试：

```powershell
uv run --frozen pytest -q -m "not cuda"
```

`nvidia-smi` 的 CUDA 信息表示驱动能力，不等于 PyTorch wheel 的 runtime，更不证明 CUDA 运算成功。

## 5. 本机验收记录

| 检查 | 当前证据 |
|---|---|
| 全新项目隔离环境 | Python 3.11.8，Torch 2.10.0+cu128 / runtime 12.8；16 个运行/测试包完成安装，离线 frozen 同步复核通过 |
| CPU FP32 | `actual_device=cpu`，前向/反向/参数更新通过；loss 0.117088 → 0.093820 |
| 5070 CUDA FP32 | `actual_device=cuda:0`，前向/反向/参数更新与同步通过；loss 0.117088 → 0.093820 |
| 5070 CUDA BF16 | 实际输出 `torch.bfloat16`、原生 BF16 支持、同步通过；loss 0.116782 → 0.093734 |
| GPU 架构 | 实测 compute capability 12.0；wheel 编译架构包含 `sm_120` |
| 自动测试 | 项目锁定环境 `13 passed, 1 warning`；真实 CUDA FP32/BF16 测试均执行，未跳过 |
| 全局 Python | 仍是原有 Torch 2.8.0+cpu，未被项目安装替换 |
| 5090 迁移 | 未执行，不阻塞 L01 |

验收依据是三份实际计算报告和完整测试结果，不仅是安装进程退出码。原始记录位于 `runs/environment-cpu.json`、`runs/environment-gpu.json`、`runs/environment-gpu-bf16.json` 和 `runs/validate-l01.stdout.log`；下载/验证后台进程已结束。

唯一测试 warning 是未安装可选 NumPy 的提示。本课只使用 PyTorch 张量计算，不调用 NumPy 桥接；不为消除提示额外引入依赖。后续数据课程需要 NumPy 时再加入并锁定版本。此前系统 CPU 环境的 11 项预检查不计入此次正式验收。

JSON 包含 Python/平台/Torch/runtime、驱动清单、设备名/显存/计算能力、Git revision/工作树状态、锁文件哈希与实际计算结果。完整日志和 JSON 保存在忽略的 `runs/`；不要提交凭据或私人路径。

## 6. 迁移到 Windows/5090

只有实测吞吐、显存或任务耗时成为瓶颈时才考虑迁移，不直接按显卡名推算训练时间。

1. 在 5090 上取得同一提交，使用同一 `pyproject.toml`/`uv.lock`，不要复制虚拟环境。
2. 记录该机 Windows 版本、GPU 完整型号/显存和驱动，检查磁盘与网络。
3. 执行第 3、4 节相同命令；JSON 应显示实际 5090，而不是沿用 5070 的报告。
4. 若驱动或运行库不兼容，先报告并让用户选择，不自动修改系统。
5. 后续训练用同一数据/tokenizer/模型配置比较，再决定是否扩大 batch 或训练规模；本课不进行性能基准。

## 7. 常见问题

| 现象 | 先检查 |
|---|---|
| `torch.version.cuda` 是空或 CUDA unavailable | 是否用了全局 Python？用 `uv run --frozen python -c "import torch; print(torch.__version__, torch.version.cuda)"` 检查项目环境 |
| 设备可见但 kernel/架构报错 | 查看探针中的 Torch/runtime/compiled architectures 与真实错误；不要以 nvidia-smi 成功盖过计算失败 |
| DLL 加载失败 | 记录缺失的 DLL 和完整错误，检查官方 wheel 的系统前置要求；不要随机复制其他项目 DLL |
| `Failed to initialize NumPy` | L01 尚未安装可选 NumPy；纯 PyTorch 探针可正常运行，不代表 CUDA 不可用 |
| hardlink 回退为 copy | uv 缓存和项目位于不同磁盘时正常回退，增加安装复制/空间开销，不代表训练计算变慢 |
| BF16 请求失败 | 查看 native_bf16 与错误；明确选 FP32 继续定位，不声称 BF16 已验证 |
| 下载超时或中断 | GPU wheel 较大，保持安装进程；使用原锁文件重试，保留日志，不关闭 TLS 验证 |
| 写报告失败 | 输出路径应为可写文件，不是现有目录；探针返回非零，不把旧报告当作新结果 |
| GPU OOM | 本课探针极小，先检查其他进程占用；后续模型阶段再通过配置调小，不自动迁移/杀进程 |

## 8. 官方入口

- [uv 安装](https://docs.astral.sh/uv/getting-started/installation/)
- [uv PyTorch 集成](https://docs.astral.sh/uv/guides/integration/pytorch/)
- [PyTorch 历史版本安装](https://pytorch.org/get-started/previous-versions/)
- [本项目 CUDA 12.8 wheel 索引](https://download.pytorch.org/whl/cu128/torch/)
- [NVIDIA 驱动](https://www.nvidia.com/Download/index.aspx)

索引中已核实 Windows CPython 3.11 的 2.10.0+cu128 wheel，并已在本机 5070 实测；不将该结果外推为其他机器或后续模型规模已经验证。
