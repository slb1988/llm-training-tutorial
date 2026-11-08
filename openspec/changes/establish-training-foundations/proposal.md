# Proposal

## Why

直接运行完整训练脚本难以分辨环境、分词、数据、模型和梯度各自的作用，也不能帮助学习者在另一台训练电脑独立复现。需要先建立逐课可验证的基础，使后续预训练、对话模型与工具使用都有清楚的数据和模型契约。

## What Changes

本 change 将实现 L01–L08；当前仅生成草案，不实施：

- 提供中文逐课教程，每课交付小实验、验证、自检问题和自主扩展入口，并与一个提交对应。
- 建立隔离环境和设备探针；将选定系统的安装、依赖重建、GPU 验证及排障写入 `docs/setup/README.md`，区分编写机和用户 5090 训练机的证据。
- 提供张量/自动微分实验，以及固定主线 tokenizer 的编解码和独立 toy BPE 学习实验。
- 提供微型公开/自写语料的校验、去重、文档级切分和 next-token batch 构造。
- 提供因果注意力实验、小型 decoder 的随机初始化、参数量检查和前向输出验证。

非目标：本阶段不运行正式预训练、SFT、LoRA、DPO、GRPO，不建设 HTTP 服务或 Agent，不下载完整语料，不承诺模型聊天质量。system/user/assistant、双协议接口、tool use 与使用后的再训练保留在总路线，进入相应阶段前另建 change。

## Capabilities

### New Capabilities

- `tutorial-learning`: 可逐课学习、验证和定位提交的课程交付，及与主线分离的自主扩展入口。
- `training-environment`: 可复现的系统/依赖安装说明，分离 CPU 与目标 GPU 的设备验证和状态记录。
- `tokenization`: 固定 tokenizer 的可检查编解码，以及不影响主线资产的独立分词实验。
- `training-data`: 可追踪的语料校验/去重/切分，以及可核对的 next-token 输入和标签。
- `language-model-training`: 本阶段仅建立小型模型的随机初始化、前向/梯度学习实验和因果性验证，为后续训练扩展同一能力。

### Modified Capabilities

无。初始化时项目没有已有 capability specs 或实现。

## Impact

- 预期新增项目依赖/锁文件、`src/llm_tutorial/`、微型测试与逐课教程；本次规划提交不创建这些实现。
- 计划复用 PyTorch、Transformers、Tokenizers、Datasets、uv 和 pytest；兼容版本在目标 OS 确认后的环境步骤验证并锁定。
- 安装说明与自主模块索引已有规划骨架，实施时就地完善，不新建一次性“完成说明”。
- 用户将在另一台 5090 电脑执行真实训练；当前没有目标机的 OS、具体显存或驱动证据。L01 实施前须确认 OS，目标 GPU 未验证时不得用本机结果标为完成。
- 运行不依赖 MiniMind 的兄弟目录。参考版本、实际引入资产的来源/许可证和哈希须记录；数据、模型权重、凭据和完整运行日志不提交。
- 本阶段无对外 HTTP API、无远端服务变更、无自动 push，也不授权修改另一台电脑。
