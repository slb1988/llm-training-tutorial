# LLM Training Tutorial

从随机权重开始，循序学习数据、分词、预训练、SFT、LoRA、DPO、评估与模型使用；后续接入 OpenAI/Anthropic 兼容接口、工具调用及有条件的在线 RL。

**L01 已完成：Windows 隔离环境与设备探针。** 本机 CPU FP32、5070 CUDA FP32/BF16 与 13 项测试通过；目前尚未下载训练数据/权重或实现 LLM 训练循环。下一课需用户确认后再开始。

## 从这里开始
- [L00：路线与学习约定](docs/lessons/00-planning.md)
- [L01：验证实际计算设备](docs/lessons/01-environment.md)
- [完整路线与调研依据](.claude/plans/LLM训练全流程教程.md)
- [首阶段 proposal](openspec/changes/establish-training-foundations/proposal.md)
- [首阶段设计](openspec/changes/establish-training-foundations/design.md)
- [首阶段任务 L01–L08](openspec/changes/establish-training-foundations/tasks.md)
- [Windows/5070 安装与 5090 迁移](docs/setup/README.md)
- [自主阅读与实现模块 M01–M12](docs/extensions/index.md)

## 学习方式
库优先；核心原理做白盒实验。每课一个目标、实验、验证和提交，结束后暂停。自主实现项由用户选择，不自动做完。

优先在本机 **Windows/5070** 开发、测试与训练；遇性能瓶颈后才由用户迁移到另一台 **Windows/5090**。两台机器的证据分别记录，5090 未验证不阻塞前期课程。

## 本阶段规划检查
在仓库根目录，使用已安装的 OpenSpec 1.16.0：

```sh
openspec status --change establish-training-foundations
openspec validate establish-training-foundations --strict
```

这些命令只检查规划状态/结构，不执行课程，也不证明 GPU 环境已就绪。

## 来源与边界
参考 [MiniMind](https://github.com/jingyaogong/minimind/tree/233d00fa068ec2b8c0d4f07b703934d6391a5a73)，不依赖其兄弟目录。当前未复制上游实现、tokenizer 或数据；后续实际引入资产时记录来源、版本和对应许可证。
