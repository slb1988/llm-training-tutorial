# 自主阅读与实现模块

这些模块是用户可选择的学习入口，不是自动执行队列。当前没有替用户实现练习代码；主线也不依赖练习完成。

- `[自主阅读]`：先读入口，再回答该课的问题。
- `[自主实现]`：独立实验或可替换模块，使用主线的测试契约对照库实现。
- `[后续决策]`：改变依赖、模型目标、协议范围或资源成本时，先提出选择。
- 新项目入口在相应课程真正创建后填写；不预先给不存在的文件标行号。

## 模块索引

下面的源码路径相对于 MiniMind；它们是阅读入口，不表示本轮已逐行审查全部实现。项目自身的路径待相应课程创建后补齐，不给不存在的文件伪造行号。

| 编号 / 前置 | `[主线]` 边界 | `[自主阅读]` 入口 | `[自主实现]` 题目与最小验收 |
|---|---|---|---|
| M01 / L03–L04 分词 | tokenizers + 固定主线词表 | `trainer/train_tokenizer.py`；HF Tokenizers 文档 | 比较不同词表的中英 token 数与往返一致性；不覆盖主线词表 |
| M02 / L05–L06 数据 | datasets + 精确去重/切分 | `dataset/lm_dataset.py` | 增加一种近重复检测或 packing 策略；验证切分不泄漏、EOS/有效 token 数正确 |
| M03 / L07–L08 模型内部 | Transformers Qwen3 + SDPA | `model/model_minimind.py` 中 Attention/RMSNorm/RoPE/MLP；Qwen3 文档 | 在 tiny 实验里逐个替换小模块，与参考实现对照输出/梯度；全手写 decoder 是进一步扩展 |
| M04 / L09–L12 训练循环 | PyTorch optimizer、AMP | `trainer/train_pretrain.py`、`trainer/trainer_utils.py` | 实现替代 LR schedule 或累积策略；测试尾批和续训，不以 loss 一次下降代替正确性 |
| M05 / L14、U01 消息与模板 | 版本化对话契约 | `dataset/lm_dataset.py`；TRL SFT 模板说明；两家 SDK 消息类型 | 增加一种等价 chat template；逐 token 验证角色边界/监督区间/生成前缀，并隔离实验模型版本 |
| M06 / L10、L21 解码 | Transformers generate | `model/model_minimind.py` 的 generate；Transformers generation 文档 | 实现小型 greedy/top-k 采样器并对照固定 logits；高级 KV cache 优化另开实验 |
| M07 / L16 LoRA | PEFT | `model/model_lora.py`；PEFT quicktour | 手写一个 Linear LoRA 实验；核对冻结参数、低秩更新与合并前后输出 |
| M08 / L17–L18、R 系列 对齐 | TRL DPO/条件启用 GRPO | `trainer/train_dpo.py`、`trainer/train_grpo.py`、`trainer/rollout_engine.py`；TRL 文档 | 先做 DPO loss 数值/梯度小实验；奖励设计与多轮 RL 属于后续决策，不直接长训 |
| M09 / U02–U05 协议 | 官方 SDK + 薄适配 | `scripts/serve_openai_api.py`；两家 SDK 的请求与事件类型 | 增加独立协议适配，如 OpenAI Responses；写清支持子集并用真实 SDK 测试，不污染推理后端 |
| M10 / T01–T03 工具 | Schema 校验 + 有界执行器 | `scripts/chat_api.py`、`scripts/eval_toolcall.py`；官方 tool-use 类型 | 添加一个无副作用工具；测试参数、调用 ID、失败和白名单；有副作用工具必须单独授权 |
| M11 / T03、U01 Agent/上下文 | 单工具串行循环、显式长度限制 | 主线 Agent 契约、调用轨迹与测试 | 实现一种上下文裁剪或多步任务策略；保留 system/调用结果关联，测试步数和预算边界 |
| M12 / T04–T06 再训练闭环 | 待审样本/版本清单，不自动训练 | 训练样本与运行 trace 的字段定义、阶段评估脚本 | 增加失败分类或候选数据筛选器；输出可审查理由，证明不吸收敏感信息和 held-out 数据 |

每课只展开相关模块，先提供必要阅读与可实现边界，不在第一天写完全部扩展教程。用户完成某项后，可以请求测试/讨论或纳入主线；不会自动触发额外 Agent 评审或重写用户实现。


## 难度与资源提示

| 模块 | 难度 | 建议资源 |
|---|---|---|
| M01 分词 | 入门 | CPU 微型语料 |
| M02 数据 | 入门到中级 | CPU；大数据处理另报预算 |
| M03 模型内部 | 中级到进阶 | tiny CPU；完整模型替代另行规划 |
| M04 训练循环 | 中级 | CPU 对照测试；性能实验才用 GPU |
| M05 消息与模板 | 中级 | CPU fixtures |
| M06 解码 | 中级 | 固定 logits 可在 CPU 验证 |
| M07 LoRA | 中级 | 小矩阵 CPU；真实微调在 5090 另测 |
| M08 对齐 | 进阶 | loss 实验可用 CPU；GRPO 需独立预算 |
| M09 协议 | 中级 | 本地假后端 + 官方 SDK，不需付费模型 |
| M10 工具 | 中级 | 无副作用本地工具 |
| M11 Agent/上下文 | 中级到进阶 | 有界循环；模型调用费用需批准 |
| M12 再训练闭环 | 中级 | 合成/公开轨迹；不能自动启动训练 |

## 阅读导航
MiniMind 入口基于固定参考版本：
[233d00f](https://github.com/jingyaogong/minimind/tree/233d00fa068ec2b8c0d4f07b703934d6391a5a73)。
不要求在运行机器上存在兄弟目录。

- [Tokenizers](https://huggingface.co/docs/tokenizers/)
- [Transformers Qwen3](https://huggingface.co/docs/transformers/v4.57.6/en/model_doc/qwen3)
- [PEFT](https://huggingface.co/docs/peft/)
- [TRL](https://huggingface.co/docs/trl/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)

具体实验会随对应课程提供输入/输出、修改范围和验收命令；不把阅读入口误当作经过本项目验证的版本组合。
