# L00：先知道要学什么

## 本课目标
建立可 review 的学习路线和首阶段 OpenSpec 草案，不开始训练实现。L00 的规划提交不表示用户已经批准执行 L01。

## 已确定
- 路线 A：成熟库搭主线，用独立实验理解模型和训练机制。
- 每课一个提交；完成后停下，理解后再继续。
- 训练从随机权重开始；后续覆盖模型调用、角色消息、工具使用与再训练。
- 真实训练在用户另一台 5090 电脑；系统环境安装说明必须落盘。
- 自主阅读与实现模块保留给用户，不预先做完。

## 地图
| 系列 | 目标 | 当前状态 |
|---|---|---|
| L01–L08 | 环境、张量、tokenizer、数据、注意力、随机模型 | 首阶段 OpenSpec 草案待 review |
| L09–L21 | 训练、评估、SFT/LoRA/DPO、导出推理 | 路线，尚未细化为执行任务 |
| U01–U06 | OpenAI/Anthropic 文本与流式调用 | 后续路线 |
| T01–T06 | Tool use、Agent、工具数据和反馈 | 后续路线 |
| R01–R03 | 奖励、rollout、GRPO | 条件启用，另行决策 |

先读 [proposal](../../openspec/changes/establish-training-foundations/proposal.md)、[设计](../../openspec/changes/establish-training-foundations/design.md) 和 [任务](../../openspec/changes/establish-training-foundations/tasks.md)。系统安装入口是 [setup](../setup/README.md)，扩展入口是 [modules](../extensions/index.md)。

## Review 重点
1. L01–L08 是否足够小，学习目标是否符合预期？
2. 库实现与自主实验的边界是否合适？
3. 5090 机器使用什么 OS/版本？这是 L01 前的决策，不用开发机情况代填。

## 自检
- 为什么“从零训练权重”不要求重写全部模型库？
- 为什么接口能调用模型，不等于模型会遵循角色或使用工具？
- 为什么一个 CPU 或假后端测试通过，不能宣称 5090 训练或模型能力已通过？

本课没有训练实验，不提供虚假的 loss、性能或显存结果。下一步须先完成 review 和目标 OS 确认。
