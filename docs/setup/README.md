# 5090 训练机：系统环境安装与复现

**状态：L00 文档骨架。尚未安装、尚未在目标机器验证；不是现在即可照抄完成安装的指南。**
用户确认目标 OS 后，L01 在本文件补齐选定平台的实际步骤，并随依赖变化持续维护。

## 1. 机器角色与待确认事实
- 编写机器：前期调研为 Windows / RTX 5070，不能代表训练机器。
- 真实训练机器：用户的另一台 5090 电脑，尚未连接或探测。
- 下一步先确认：Windows 原生、WSL2 或 Linux，以及版本。
- 首次设置记录：GPU 完整型号/显存、驱动、已有 Python/uv、可用磁盘与网络条件。未核实的值留空，不默认 32GB 或任意驱动版本。

## 2. L01 必须补齐的安装内容
| 顺序 | 文档交付 | 验收 |
|---|---|---|
| 1 | 目标 OS 与所需系统组件、管理员权限边界 | 用户确认路线；不擅自安装 WSL 或升级驱动 |
| 2 | Git checkout、Python 与 uv 安装/检查、项目虚拟环境 | 从任意 checkout 路径可操作，不依赖编写机绝对路径 |
| 3 | 支持目标 5090 的 PyTorch CUDA 构建及兼容驱动、安装来源 | 版本组合有官方依据和实际运行证据，不复制旧 requirements |
| 4 | 项目依赖与锁文件的安装/重建步骤 | 干净虚拟环境可复现；不污染系统 Python |
| 5 | CPU tiny 与 5090 GPU 验证命令、预期输出、失败判定 | 不只 import 成功或退出码为 0；有真实前后向结果 |
| 6 | 常见问题与恢复步骤 | CPU wheel 误装、驱动/wheel 不匹配、OOM、下载失败能定位 |
| 7 | 跨机复现和运行记录 | 相同 Git revision、依赖、数据/tokenizer 配置可追踪 |

源码构建或需要自定义 CUDA 扩展时才评估额外 toolkit。使用预编译 PyTorch wheel 不等于默认要另装完整 CUDA Toolkit；具体仍以所选版本官方要求为准。

## 3. 验证层级
1. **系统可见**：采集 GPU/驱动。可先在目标机器手动运行以下只读命令：

   ```sh
   nvidia-smi
   python --version
   uv --version
   ```

   命令不存在也应如实记录，不自动安装。分享结果前去除不必要的个人目录或设备标识。

2. **运行时可用**：L01 的探针必须报告 Python、PyTorch、wheel CUDA runtime、设备名称与能力；当前还没有这个探针。
3. **真正执行**：小张量 CUDA forward/backward/optimizer step、结果有限、同步完成，检查是否真的在目标 GPU 上执行。
4. **精度与课程档位**：根据实际支持选择 BF16/FP32 等路径，记录能力和结果；不把不支持的精度静默当成已验证。
5. **后续训练预算**：L12/L13 再测 tokens/s、峰值显存和配置，用户批准后开始更大规模训练。

`nvidia-smi` 中的 CUDA 版本信息不是已安装的 PyTorch runtime 版本，更不能独立证明 PyTorch 能在 5090 上运行。

## 4. 目标机器验收记录要求
实际验证时记录 OS/版本、GPU/显存/驱动、Python、PyTorch/runtime、依赖锁版本、Git revision、所用命令和结果。可复现摘要入文档，完整运行日志放忽略的 `runs/`，不提交凭据和私人路径。

| 项目 | 当前证据 |
|---|---|
| OS/版本 | 待用户确认 |
| GPU 完整型号/显存 | 用户说明为 5090，其他待实测 |
| 驱动 / CUDA wheel | 未选择、未验证 |
| CPU tiny | 未执行 |
| 5090 CUDA 前后向 | 未执行 |
| 安装复现 | 未执行 |

用户可在目标机执行后回传必要输出；助手不能把未接触机器的验证记为成功。L01 的目标 GPU 验收未完成时，任务保持未完成/说明阻塞。

## 5. 官方入口
- [uv 安装](https://docs.astral.sh/uv/getting-started/installation/)
- [PyTorch 官方安装选择](https://pytorch.org/get-started/locally/)
- [NVIDIA 驱动](https://www.nvidia.com/Download/index.aspx)

这里只提供后续核实入口，不声称已经验证这些页面当前列出的版本适合目标机。
