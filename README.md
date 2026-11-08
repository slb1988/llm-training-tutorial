# LLM Training Tutorial

从随机权重开始，循序学习数据、分词、预训练、SFT、LoRA、DPO、评估与模型使用；后续接入 OpenAI/Anthropic 兼容接口、工具调用及有条件的在线 RL。

**当前是 L00：规划仓库，不是可运行的训练工程。** 已初始化 OpenSpec，首阶段草案待 review；没有安装训练依赖、下载数据或执行训练。

## 从这里开始
- [L00：路线与学习约定](docs/lessons/00-planning.md)
- [完整路线与调研依据](.claude/plans/LLM训练全流程教程.md)
- [首阶段 proposal](openspec/changes/establish-training-foundations/proposal.md)
- [首阶段设计](openspec/changes/establish-training-foundations/design.md)
- [首阶段任务 L01–L08](openspec/changes/establish-training-foundations/tasks.md)
- [5090 训练机系统环境安装文档](docs/setup/README.md)（当前为待确认/待验证骨架）
- [自主阅读与实现模块 M01–M12](docs/extensions/index.md)

## 学习方式
库优先；核心原理做白盒实验。每课一个目标、实验、验证和提交，结束后暂停。自主实现项由用户选择，不自动做完。

真实训练在另一台 **5090** 电脑；操作系统、显存与驱动还未核实。开发机器的测试不能替代目标机器验收。环境安装文档会随 L01 及后续依赖变化维护。

## 本阶段规划检查
在仓库根目录，使用已安装的 OpenSpec 1.16.0：

```sh
openspec status --change establish-training-foundations
openspec validate establish-training-foundations --strict
```

这些命令只检查规划状态/结构，不执行课程，也不证明 GPU 环境已就绪。

## 来源与边界
参考 [MiniMind](https://github.com/jingyaogong/minimind/tree/233d00fa068ec2b8c0d4f07b703934d6391a5a73)，不依赖其兄弟目录。当前未复制上游实现、tokenizer 或数据；后续实际引入资产时记录来源、版本和对应许可证。
