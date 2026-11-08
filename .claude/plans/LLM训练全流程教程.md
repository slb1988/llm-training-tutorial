# LLM 训练全流程教程：总路线与调研依据

状态：**用户已 review 首阶段，优先使用本机 Windows/5070 开发、测试与训练；另一台 Windows/5090 仅在性能瓶颈后迁移。当前按单课推进 L01，完成状态以 OpenSpec tasks 为准。**

本文件是总路线与调研依据；当前阶段的执行任务仅以 `openspec/changes/establish-training-foundations/tasks.md` 为准，不维护第二份完成状态。L01 只建设隔离环境与小型设备探针，不下载语料/模型权重或执行正式训练；自主扩展不默认由助手实现。

## 1. 目标与边界

在 `D:\Github\minimind` 的平级目录建立独立教学 Git 仓库，逐步完成：

```text
corpus -> tokenizer -> batches -> random-init LM -> pretrain -> SFT -> DPO
                                                           |
                                                           v
                         evaluate -> export -> inference -> API -> agent/tool use
                             ^                                       |
                             |                                       v
                             +--- reviewed SFT/DPO/(future GRPO) <- curated traces
```

LoRA 是 SFT 等训练的可选参数高效实现，不是额外必经阶段。图中的反馈环必须经过数据筛选、评估和用户批准，不是边使用边自动更新权重。

- 从随机权重开始训练，而不只是给现成模型做 LoRA。
- 按 tutorial 学习：每课一个明确问题、可运行实验、可解释的结果、测试和一个 Git 提交。
- 小型独立模块优先采用成熟第三方库；不把实现整套训练框架作为学习前提。
- OpenSpec 定义阶段目标、可观察行为、设计与任务；用户决定关键取舍。
- 每次只推进一个获准的教学步骤，完成后停下；不因存在 tasks 就自动实施整个阶段。
- 覆盖训练、使用与后续再训练；DPO 是离线偏好优化，在线 RL 单独安排，不混为一谈。
- 模型使用包括 Python/CLI、多轮消息、OpenAI Chat Completions 与 Anthropic Messages 的明确兼容子集；云端模型调用作为可选对照，不偷偷替换本地模型。
- 从 SFT 阶段就支持 `system` / `user` / `assistant`；后续扩展工具调用和结果消息，不等到 Agent 阶段才重做数据格式。
- 第一版不以“达到可用通用聊天模型质量”作为承诺；协议兼容、运行机制和模型能力分别验收。
- 可以细化的模块提供自主阅读与实现入口；主线提供可运行基线，不能把必需的正确性或安全处理留成用户填空。

本项目以训练全流程为主线；API、Agent 是模型使用与再训练闭环的后续课程，不扩展成通用应用开发框架。

## 2. 调研事实

### 2.1 MiniMind 本地基线

- 路径：`D:\Github\minimind`，工作树干净，调研中未修改。
- 版本：`233d00fa068ec2b8c0d4f07b703934d6391a5a73`。
- 来源：<https://github.com/jingyaogong/minimind>，代码许可证 Apache-2.0；数据许可证仍需分别核实。
- 当前主线为 MiniMind-3：Dense 约 64M，默认 hidden size 768、8 层、词表 6400；不是早期 26M 教程配置。
- 包含 tokenizer、原生 PyTorch 模型、预训练、SFT、LoRA、DPO、PPO/GRPO、蒸馏和推理等参考代码。
- `dataset/lm_dataset.py` 分别实现预训练标签和 assistant-only SFT 标签；`model/model_minimind.py` 在 loss 内部做 next-token shift。
- Tokenizer 训练使用 Hugging Face `tokenizers`；上游明确提示重训 tokenizer 会影响已有模型复用。
- README 标注 mini 预训练数据约 1.2GB、mini SFT 数据约 1.6GB，不能当成第一课的微型数据。
- README 开头将“2 小时”说明为 3090 上 SFT 的口径，训练开销表又给出预训练 + SFT 约 2.31 小时估算。不能把宣传数字当成本机完整训练的承诺。
- `requirements.txt` 同时包含训练、服务、UI、评估等依赖，不适合教学工程整份照搬；Torch 条目还是注释，不能据此认定 GPU 环境已就绪。

### 2.2 本机初始环境记录（L01 安装前）

| 项目 | 实测 | 含义 |
|---|---|---|
| GPU | NVIDIA RTX 5070，12227 MiB | 用户指定的首选开发、测试与可承受训练目标；不代表 5090 已测 |
| Python | 3.11.8 | 可作为隔离环境候选 |
| 当前解释器的 Torch | 2.8.0+cpu，CUDA unavailable | 不是显卡不支持，而是当前安装并非 CUDA 构建 |
| uv | 已存在 | 可使用项目级虚拟环境和锁文件 |
| OpenSpec | 1.16.0 已安装 | 不需要为了本项目额外包装一个规划框架 |
| WSL 发行版列表 | 仅发现 docker-desktop | 未发现现成的普通 Ubuntu 开发发行版；不自动安装 |

以上为本机初始环境记录；隔离环境的实际版本和验证结果见 `docs/setup/README.md`。5090 仍未验证，正式训练预算必须以当前机器实测为依据。

### 2.3 已确认的训练部署要求

- 当前优先在本机 Windows 11 x64 / RTX 5070 上开发、测试与训练；只有实测性能瓶颈出现后，才由用户转到另一台 Windows/5090 操作。
- 5090 的 Windows 具体版本、显存、驱动和运行时仍待迁移时核实；不访问远端，也不以本机结果宣称后备机器已验证。
- 系统环境安装说明落盘到 `docs/setup/README.md`，覆盖本机安装/复现、GPU 验证、排障和未来 5090 迁移，并随依赖变化维护。
- L01 验收本机 CPU 与 5070 CUDA 的真实计算；5090 未验证不阻塞本课。后续换机器时按同一提交和锁文件重新验证，不复制 `.venv`。
- 吞吐、峰值显存和长训预算在对应课程实测；不因为有后备 5090 就自动扩大数据或任务。

## 3. 已确认路线 A：库优先 + 核心白盒实验

- 主线使用 Transformers 原生小型 Qwen3 随机初始化，保留 PyTorch 最小训练循环，再接 PEFT/TRL。
- “从零训练”要求权重随机初始化，不要求手写矩阵乘法、BPE、优化器或整套模型库。主线不加载现成模型权重；外部模型作为对照时明确标识。
- 仍学习张量维度、因果注意力、RoPE/RMSNorm/MLP、next-token loss、反向传播、数据、评估与 checkpoint，而非只调用 `trainer.train()`。
- 原路线 B 的逐层手写模型，降为用户自主扩展；原路线 C 的直接 fork MiniMind 不作为主线。扩展模块见第 7 节。

## 4. 设计方案（路线 A；新增范围待 review）

### 4.1 项目与复用边界

已确认项目目录：`D:\Github\llm-training-tutorial`，独立 Git 仓库；训练机器上的 checkout 位置可不同。不改 MiniMind，不依赖兄弟目录的 `sys.path`、开发机绝对路径或可变源码。

| 模块 | 建议复用 | 自己保留的教学内容 |
|---|---|---|
| 依赖与环境 | uv、项目虚拟环境 | 环境探针、CPU/GPU 档位 |
| 张量/自动微分/优化器 | PyTorch | 一次 forward/backward/update 和最小训练循环 |
| 分词 | tokenizers、Transformers tokenizer | 编解码、特殊 token、一个独立微型 BPE 训练实验 |
| 语料 | datasets、Python 标准库 | 数据格式、来源记录、精确去重、分组切分、采样与质量检查 |
| 主线模型 | Transformers `Qwen3Config` / `Qwen3ForCausalLM` | 小配置随机初始化、模块与张量可视化，不直接导入 MiniMind 权重 |
| 注意力计算 | PyTorch SDPA | 一个小矩阵实验讲清 causal mask，生产路径不重写高性能 kernel |
| SFT | 先理解标签，再接 TRL SFTTrainer | assistant-only mask、模板一致性和训练前后对照 |
| LoRA | PEFT | 低秩原理、冻结 base、adapter 保存/加载 |
| DPO | TRL DPOTrainer | 偏好数据、policy/reference、目标函数与 held-out 对照 |
| 记录与测试 | 本地 JSONL、pytest，绘图按需 | loss、tokens/s、峰值显存、数据/模型版本追踪 |
| 导出推理 | Transformers、safetensors | 权重/tokenizer/config 成套导出与重新加载 |
| 模型调用客户端 | 官方 `openai` / `anthropic` SDK | 本地服务验收、可选远端模型对照，不重写 HTTP SDK |
| 兼容服务 | 候选 FastAPI/Pydantic、Starlette 流式响应 | 小型协议适配层，与推理后端分离；不造通用 API 网关 |
| 工具描述与校验 | JSON Schema、jsonschema/Pydantic | 工具注册、调用/结果关联与最小执行边界 |
| 后续在线 RL | TRL GRPOTrainer，版本能力需实测 | 奖励、rollout、策略版本与有效 token mask，不重写训练算法 |

不在起步时引入 Hydra、DeepSpeed、vLLM、在线实验平台或完整训练调度框架。服务阶段再加 HTTP 依赖；分布式或更大规模训练真正需要时，再引入 Accelerate 等组件。正式兼容服务实现前优先验证现成组件能否满足子集，只保留必要的薄适配，不为了教学重复实现网络栈。

库版本：不照搬上游 requirements，也不把各库最新版本任意拼在一起；环境步骤验证组合后锁定，后续按阶段增量添加依赖并复测。当前在线文档是调研依据，不是已经通过兼容测试的版本组合。

### 4.2 模型、tokenizer 与运行档位

- 主线优先复用固定版本的 MiniMind tokenizer；记录来源、文件哈希和许可证。
- 单独训练 toy tokenizer 用于学习，不覆盖主线 tokenizer；改变词表意味着新的模型实验谱系，不能直接接着训练旧 checkpoint。
- Qwen3 配置显式设置词表大小、特殊 token ID、head dimension、层数等，避免把大模型默认值意外带入。
- `tiny`：示例配置 2 层、hidden 128、序列 64–128；面向 CPU 测试和机制验证，不评价聊天能力。
- `learn`：通过 tiny 后按 GPU 探针选择，例如约 10M–30M 参数、短上下文；实际参数量在课程中计算，显存和吞吐实测。
- `reference`：可选约 64M 的上游规模对照；不承诺新实现与上游 checkpoint 数值或权重格式完全相同。
- 所有训练入口有明确 `max_steps` / 样本或 token 上限。下载规模、长训时间和远程费用到需要时先让用户决定。

### 4.3 数据与模板

- 起步使用可入库的自写微型 fixtures；真实语料采用核实许可后的公开样本，不默认读取个人知识库或历史聊天。
- 数据流程：来源登记 -> 格式检查 -> 清洗/去重 -> 按文档或会话分组切分 -> tokenizer/分块。先切分再分块，避免同源内容混入 train/validation/test。
- tokenizer 学习实验只用训练切分，不能通过 tokenizer 训练泄漏验证集。
- 验证集用于过程选择，最终测试集保留到阶段验收；真实数据近重复污染另行检查，不声称精确哈希去重解决全部泄漏。
- 初始 SFT 就覆盖 `system` / `user` / `assistant` 和多轮对话；工具消息在后续 T 阶段扩展，thinking 与多模态不进入初始范围。
- API 的 `role` 字段、模板中的角色文本/分隔标记、tokenizer 的特殊 token 是不同层次；不是给词表加一个 `system` 标签就自动获得指令遵循能力。训练与推理共用版本化模板，并用行为样本评估角色遵循。
- 工具阶段将结构化调用与结果作为对话内容建模：assistant 的工具调用是监督目标，user/system/tool result 通常不计入 assistant-only loss；实际 mask 必须逐 token 验证。
- MiniMind 的原始对话字段转换为库接受的格式；字段重命名之外还要检查模板、结束标记与 loss mask。
- TRL 的 assistant-only loss 依赖能返回 assistant 区间的模板。上游 MiniMind 模板不能未经检查就认为兼容；对实际 token/labels 做断言，并明确排除 user/system/pad。
- 模型内部做 next-token shift 时，collator 不再重复 shift。PAD 与 EOS 的语义分别处理，不因 padding 误屏蔽有效结束标记。

### 4.4 训练与评估闭环

```text
random init -> pretrain checkpoint -> full SFT -> DPO -> export
                            |
                            +-> LoRA SFT (alternative branch)
```

LoRA 是参数高效训练方式，不是全参 SFT 之后必须追加的一道阶段。用于比较时从同一 base、同一数据任务开始；DPO 主线从明确的 SFT checkpoint 出发。

- 每个训练阶段都记录训练前后的固定样本和持出数据指标，不到最后才补评估。
- 单 batch 过拟合证明数据、梯度和 loss 链路能工作，不证明泛化。
- PPL 基于相同 tokenizer、相同数据、相同有效 token mask 的平均 NLL；不同 tokenizer 的 PPL 不直接横比。
- SFT 看指令响应与 held-out assistant loss；DPO 看 held-out 偏好结果以及能力退化，不把训练 reward/margin 上升等同于全面进步。
- checkpoint 保存模型、优化器、调度器、step、随机状态和数据进度；先在 CPU 确定性 tiny 用例上验证续训，再对 GPU 采用说明清楚的容差。
- 运行记录包含 Git revision/工作树状态、数据与 tokenizer 标识、配置、seed、依赖版本和硬件。
### 4.5 模型使用分层：训练、推理、协议互不绑死

```text
SDK / CLI -> protocol adapter -> conversation -> template/tokenizer -> local model
                 ^                    |                                   |
                 |                    +-> reviewed training samples       v
                 +---------------- normalized generation events <---------+

agent client -> model response -> validate tool request -> execute allowed tool
      ^                                                       |
      +---------------------- tool result ---------------------+
```

- 对话领域层保存有序消息和内容块，先支持文本，后增加 `ToolCall` / `ToolResult`；保留调用 ID、工具名、参数和错误结果，不把所有内容拼成一个字符串。
- 模板负责把领域消息转换为模型可学习的 token 序列。模板与 tokenizer 标识随模型发布，训练和推理不能各维护一份不一致的格式。
- 推理后端负责生成、上下文上限、停止原因、token 使用统计；不理解某个供应商的 HTTP 字段，不执行工具。
- 协议适配层转换请求、响应和流事件。OpenAI/Anthropic 的差异留在适配器，不进入训练代码。
- 调用端优先使用官方 SDK；可显式选择本地自训模型或远端对照模型，不自动 fallback、不把远端生成结果说成本地模型能力。该接口不是建设代理网关的授权。
- 请求超过模型上下文上限时明确报错，初版不静默删除 system 或历史消息。上下文摘要、裁剪策略留作自主扩展并单独评测。

### 4.6 OpenAI / Anthropic 的兼容边界

“兼容”指锁定版本的官方 SDK 能调用已声明的功能，不宣称完整复制两个平台。

| 项目 | OpenAI 路线 | Anthropic 路线 |
|---|---|---|
| 初始端点 | `POST /v1/chat/completions` | `POST /v1/messages` |
| system | `messages` 中的 system 消息 | 顶层 `system`，不是消息列表中的 system role |
| 普通对话 | user/assistant 消息 | user/assistant 消息，文本内容块 |
| 工具调用（T 阶段） | assistant `tool_calls`，参数为 JSON 字符串 | assistant 内容块 `tool_use`，input 为对象 |
| 工具结果（T 阶段） | role=tool，使用 `tool_call_id` 关联 | user 内容块 `tool_result`，使用 `tool_use_id` 关联 |
| 流式输出 | SSE choice delta、finish reason、结束标记 | SSE message/content-block 的 start/delta/stop 生命周期 |
| 官方 SDK 验收 | `client.chat.completions.create(...)` | `client.messages.create(...)`，含 `stream=True` |

实施时锁定 SDK/API 版本并记录支持范围。不能把 Anthropic 服务做成只换 URL 的 OpenAI 服务：字段、内容块、请求头和流事件都需按各自契约处理。

- U 阶段先支持文本、多轮、system、阻塞和流式调用；T 阶段增加串行工具调用闭环。
- 第一版不包含 OpenAI Responses API、developer role、并行工具、图像/音频、Anthropic 扩展思考、缓存控制或各类 beta 特性；遇到未支持的角色、内容类型或影响语义的参数明确拒绝，不能静默丢弃或伪装支持。
- `model` 必须解析到明确的模型版本；使用统计来自实际 token 计数，不伪造 usage。特殊停止原因按协议映射，不能把长度截断都报成正常结束。
- 初始服务只监听 loopback，凭据与日志脱敏；向其他机器开放、认证和并发部署另需用户确认。
- 最小验收使用真实官方 SDK + 本地 HTTP 服务。确定性假后端验证协议，tiny 自训模型验证集成，两者分开标识；通过假后端不等于模型质量合格。
- SSE 必须验证 SDK 可以实际消费、结束与断开能正确处理；工具参数的中间 JSON 片段不能提前执行。

### 4.7 Tool use：三种能力分别交付

1. **协议能力**：能收发 tools、调用和结果，保留结构及 ID。
2. **运行时能力**：Agent 能执行“请求模型 -> 校验调用 -> 执行工具 -> 回传结果 -> 再请求模型”的有限循环。
3. **模型能力**：模型能根据任务选对工具、生成合规参数、利用结果完成回答。需要训练和持出评估，不由前两项自动获得。

先使用确定性模型替身和无副作用工具（如显式加法函数、固定表查询）验证闭环，再测真实自训模型。初始按每轮至多一次调用的串行子集实现，不自动执行模型输出中的 Python、shell 或任意 `eval`。

主线必须包含：工具白名单、JSON Schema 参数校验、调用/结果 ID 校验、步数和 token 预算、超时、失败结果、重复调用终止，以及对有副作用工具的审批边界。工具输出是外部数据，不能转换成 system 指令或扩大工具权限；模型行为测试不能代替代码侧执行约束。

服务只返回模型的调用请求，不自行执行工具。Agent 执行器独立，便于以后换模型、协议或工具库。

### 4.8 使用后的再训练：按失败类型选择方法

```text
versioned rollout -> consent/redaction -> reviewed dataset -> selected training
       ^                                                         |
       |                                                         v
       +---- approved model promotion <- held-out evaluation <- candidate
```

- 缺失或错位的消息标签：先修数据/模板契约，不立即靠 RL 弥补。
- 工具选择、参数和调用格式不稳定：先补工具示范数据，用 SFT 或 LoRA 做针对性训练。
- 有可信 chosen/rejected 偏好：可以考虑 DPO；不把所有失败日志直接当 rejected。
- 有可靠可验证奖励，且基础 SFT 能完成任务：再考虑 GRPO/在线 RL；算法、预算和目标由用户决定。
- 知识不足可能需要语料或检索，不默认用 RL 学事实；是否增加持续预训练另行决策。

轨迹记录模型/模板/工具版本、任务、调用与结果、终止原因、评估值和数据许可。默认使用公开或合成任务；真实用户聊天不自动转训练数据，也不上传到教师 API。

训练任务与正在提供服务的模型隔离。候选模型通过固定 held-out 评测、角色/工具契约回归和成本评估后，由用户批准切换；保留原模型可回退。能重新训练不等于允许后台自我训练。

在线 RL 的工具结果来自环境，不能当成策略自己生成的 action token 优化；rollout 必须绑定实际行为策略版本，不能拿旧日志直接冒充当前 on-policy 数据。采用库的相应接口并用微型实验检查这些边界。
## 5. OpenSpec 使用方式

本项目已初始化本地 OpenSpec；CLI 返回的 root 必须是本仓库。只创建首阶段 `establish-training-foundations` 的正式草案，其余阶段保留为路线。文档齐备或格式校验通过不代表用户已经批准实施。

### 5.1 规划与实施边界

1. 确认目标目录与独立 Git 仓库；获得 OpenSpec 初始化授权。
2. 在目标目录执行 `openspec init --tools pi --language zh`；如用户需要其他客户端再决定，不自动生成全部客户端文件。
3. 用 `openspec context --json` / `openspec list --json` 确认返回的 root 确实指向本项目；若解析到其他 store，先停下处理，不在错误根创建 change。
4. `openspec new change <阶段名称>` 创建带元数据的 change，不手工伪造目录。
5. 依据 `status` 和各 artifact 的 `instructions`，按依赖生成 proposal、specs、design、tasks。
6. 执行 `openspec validate <阶段名称> --strict`，把完整草案交给用户 review。校验通过只证明格式/规范检查，不等于学习设计或代码已经验收。
7. review 通过后才开始指定的一课；禁止一条 apply 把全部任务做完。

### 5.2 总路线与阶段 change

用总路线说明全貌，仅把当前阶段细化为可执行任务，后续阶段在进入前重新确认范围。

| 建议 change | 对应课程 | 边界 |
|---|---|---|
| `establish-training-foundations` | L01–L08 | 环境、张量、分词、数据、随机初始化模型 |
| `build-pretraining-loop` | L09–L13 | 最小训练、评估、续训、单卡训练与预训练 |
| `add-supervised-adaptation` | L14–L16 | 对话标签、全参 SFT、LoRA 对照 |
| `add-preference-alignment` | L17–L18 | 偏好数据与 DPO |
| `evaluate-and-export` | L19–L21 | 汇总评估、导出、干净进程推理 |
| `serve-chat-protocols` | U01–U06 | 模型使用、两种协议的文本调用/流式调用、官方 SDK |
| `add-tool-interactions` | T01–T03 | 工具契约、工具流事件、有边界的 Agent 循环；后续阶段 |
| `train-tool-behavior` | T04–T06 | 工具样本、工具 SFT、使用反馈与候选模型评估；后续阶段 |
| `explore-online-reinforcement` | R01–R03 | 奖励、rollout、GRPO；仅做路线预留，启用前另行批准 |

初始 L00 单独提交规划与课程约定。以后各阶段的 planning artifacts 先写草稿、review，通过后与该阶段首课一起入库，避免每个勾选框都变成额外提交；如用户希望规划也独立提交，再调整编号。阶段完成后的归档遵循 review 要求，尽量纳入该阶段末课提交。

推荐 specs 按稳定能力组织，例如 `tutorial-learning`、`training-data`、`language-model-training`、`model-evaluation`、`model-artifacts`，逐阶段增加 `conversation-format`、`model-serving`、`tool-interaction` 与 `training-feedback`，而不是“一课一个 spec”。只为当前新增行为写 delta，不能提前把未实现能力标为完成。

自主阅读/实现项记入 `docs/extensions/index.md`，不混入当前 change 的未完成 checkbox。只有用户选择了某项，才建立对应 OpenSpec change 或纳入明确批准的阶段；标注“自主实现”不是把工作自动派给助手。

### 5.3 每课一个 task、一个提交

一个 checkbox 对应一课；代码、测试、教程和该任务完成状态在同一提交。示例仅说明格式，非已生成的正式 tasks：

```markdown
## 1. Environment

- [ ] 1.1 L01 建立 Windows 隔离环境、设备探针和安装文档；验收：本机 CPU 与 5070 CUDA 真实前后向分别记录，5090 迁移说明不冒充实测；提交 lesson-01。

## 2. Tensor basics

- [ ] 2.1 L02 实现标量/小矩阵自动微分实验；验收：解析梯度与 autograd 对照通过，一次参数更新改变 loss；提交 lesson-02。
```

## 6. 课程与提交草案

路线 A 保留 **22 个训练基础检查点 L00–L21**，增加模型使用 U 系列、后续工具学习 T 系列，以及条件启用的强化训练 R 系列。每个检查点一个提交，不是本轮全部执行清单。若一课实际过大，应先提出拆分并经用户确认，不为了维持编号把多个学习目标硬塞进一个提交。

| 编号 / 提交标识 | 学习问题与交付 | 最小验收 |
|---|---|---|
| L00 `lesson-00` | 独立仓库、课程约定、总路线、安装文档骨架及首阶段 OpenSpec 草案 | 初始化已授权；草案供 review；strict validate 通过；不代表批准 L01 实施 |
| L01 `lesson-01` | Windows 虚拟环境、最小依赖、探针与系统安装文档 | 文档可复现；本机 CPU/5070 的真实前后向与更新通过；5090 单独待迁移验证 |
| L02 `lesson-02` | 张量、梯度、一次 optimizer update | 小例子的解析梯度与 autograd 一致，能解释梯度形状和更新方向 |
| L03 `lesson-03` | 使用 tokenizer，查看中英文本、角色分隔与特殊 token | 区分 role 字段、模板字符串和 token ID；round-trip、ID 范围及文件哈希检查 |
| L04 `lesson-04` | 用 tokenizers 训练独立 toy BPE | 保存/重载一致；输出与主线 tokenizer 隔离；只使用训练语料 |
| L05 `lesson-05` | 文本数据格式、来源、去重、分组 train/val/test 切分 | 同源文档不跨切分；非法记录可定位；采样可复现 |
| L06 `lesson-06` | 文本到 batch，next-token 标签、EOS/PAD | 对手工小样本逐 token 核对输入/目标；loss 有效 token 数正确；只 shift 一次 |
| L07 `lesson-07` | 因果 Attention 与 decoder 内部的数据流实验 | 修改未来 token 不改变过去位置输出；能读懂 Q/K/V 及模块输入输出形状 |
| L08 `lesson-08` | 小型 Qwen3 随机初始化，参数量与 forward | 无预训练权重下载；logits 为 `[B,T,V]`；loss 有限；模型与 tokenizer 相容 |
| L09 `lesson-09` | 最小 PyTorch 训练循环，故意过拟合一小批数据 | loss 在固定用例上显著下降，梯度和参数确实更新；明确这不是泛化测试 |
| L10 `lesson-10` | 持出集 NLL/PPL、固定 prompt 生成和随机模型基线 | 按有效 token 加权；相同配置下可复算；eval 不更新参数 |
| L11 `lesson-11` | checkpoint 与断点续训 | CPU tiny 上比较连续 N 步与中断恢复至 N 步的状态/输出，覆盖优化器和数据进度 |
| L12 `lesson-12` | 单卡训练效率：梯度累积、混合精度、学习率 | 尾批更新不丢；记录吞吐和峰值显存；不支持 BF16 时明确回退而非静默误用 |
| L13 `lesson-13` | 从 tiny 扩展到有预算的小规模预训练 | 先给探针测量和预计预算让用户批准；产出 checkpoint、held-out 指标及生成对照 |
| L14 `lesson-14` | system/user/assistant 的对话契约、模板与 assistant-only 标签 | 多轮角色保序；训练/推理模板一致；user/system/pad 不计 loss；存在有效 assistant token；截断行为明确 |
| L15 `lesson-15` | 从预训练 checkpoint 做全参 SFT | TRL 小样本训练通过；保存/重载后同配置评估；不要求真实数据效果必然提升 |
| L16 `lesson-16` | 从同一预训练 base 做 PEFT LoRA SFT 对照 | base 未被更新，adapter 有变化；adapter 重载输出一致；记录可训练参数比例 |
| L17 `lesson-17` | 偏好数据与 DPO 单样本数学实验 | prompt/chosen/rejected 校验；能解释 policy/reference 和目标函数符号 |
| L18 `lesson-18` | 从 SFT checkpoint 做 TRL DPO | reference 不更新；微型训练可运行；记录 held-out 偏好与原能力对照，保留负结果 |
| L19 `lesson-19` | 统一比较随机、预训练、SFT、LoRA、DPO | 同一可比评估协议出表；分开汇报质量/速度/显存；明确数据量和局限 |
| L20 `lesson-20` | 导出标准模型包、tokenizer 与配置 | 非续训用推理产物与训练 checkpoint 区分；保存/加载 logits 在容差内一致 |
| L21 `lesson-21` | 在干净进程中运行 CLI 推理，串起全流程 | 不依赖训练时内存或兄弟目录；固定 seed/解码配置下复现；tiny 全链 smoke 可运行 |

### 模型使用：U 系列，纳入学习路线

| 编号 / 提交标识 | 学习问题与交付 | 最小验收 |
|---|---|---|
| U01 `use-01` | 可调用的模型推理接口、多轮会话、生成参数与版本标识 | L14 对话契约可用于推理；system 不被丢弃；上下文溢出明确报错；不混用其他模型输出 |
| U02 `use-02` | OpenAI Chat Completions 文本兼容端点 | 官方 OpenAI SDK 实际调用本地服务；阻塞回答、模型 ID、停止原因及错误响应符合声明子集 |
| U03 `use-03` | Anthropic Messages 文本兼容端点 | 官方 Anthropic SDK 实际调用；顶层 system 与消息内容块映射正确；非纯 URL 改名 |
| U04 `use-04` | OpenAI 文本 SSE | SDK 接收增量、正确结束；断开后停止本次生成；流式/阻塞的归一化结果可对照 |
| U05 `use-05` | Anthropic 文本 SSE | SDK 可消费 message/content-block 生命周期；内容、停止原因和 usage 对应实际生成 |
| U06 `use-06` | 官方 SDK 调用示例与本地/可选远端模型对照 | 两种 SDK 的本地示例离线可跑；远端测试默认关闭，须用户提供配置/费用授权；无静默 fallback |

### 未来 Tool use：T 系列，分阶段进入，不一次性实现

| 编号 / 提交标识 | 学习问题与交付 | 最小验收 |
|---|---|---|
| T01 `tool-01` | 领域层工具描述、调用/结果与两种协议映射 | OpenAI tool_calls/tool 与 Anthropic tool_use/tool_result round-trip；ID、顺序和 JSON 类型保真；不支持的并行调用明确拒绝 |
| T02 `tool-02` | 两种协议中的工具流式事件 | 各自 SDK 能拼出完整调用；参数分片未结束时不执行；错误/不完整 JSON 被阻止 |
| T03 `tool-03` | 有界 Agent 循环与纯函数工具 | 确定性模型替身跑通调用/结果/最终回答；白名单、参数、步数、超时和失败测试通过；真实模型另报成功率 |
| T04 `tool-04` | 角色与工具调用示范数据 | 任务级 train/val/test 隔离；调用/结果 ID 闭合；仅 assistant 文本与调用参与目标 loss；环境返回值不冒充策略输出 |
| T05 `tool-05` | 工具使用 SFT/LoRA 与持出评测 | 报告调用格式、工具选择、参数、任务成功率、无须工具时的误调用和循环次数；参数更新方案先由用户选择，不承诺小模型必然学会 |
| T06 `tool-06` | 从使用轨迹到再训练候选的可审查闭环 | 日志脱敏、数据筛选和版本可追踪；可生成待审数据集；未经批准不启动再训练、不切换服务模型 |

### 后续强化训练：R 系列，条件启用

| 编号 / 提交标识 | 学习问题与交付 | 启用门槛与最小验收 |
|---|---|---|
| R01 `rl-01` | 设计可验证任务、奖励与失败用例 | 用户先选训练目标；正确性/格式/工具成本分开记录；奖励不能仅因“调用过工具”而增加 |
| R02 `rl-02` | 与行为策略版本绑定的 rollout 与奖励实验 | 固定环境可重放；工具结果不算 action token；有效奖励有区分度；报告时间/显存预算后再批准训练 |
| R03 `rl-03` | 使用 TRL 做小规模 GRPO 与回归对照 | 与 SFT baseline 比较 held-out 任务与原能力；记录失败/退化和回退；真实工具多轮支持以锁定版本探针为准 |

以上只定义未来路线，不把 R 系列标为当前待执行任务，也不把 DPO 自动换成 GRPO。每个系列的 tutorial、测试和对应任务状态随该课提交。

### 每课教程固定结构

1. 今天只解决的问题、必要前置知识。
2. 最少概念，以及张量/数据如何流动的具体例子。
3. 本提交新增文件与可直接复制的命令。
4. 应观察的结果、如何区分正常与失败。
5. 一个小实验：改变单个变量并预测结果。
6. 2–3 个自检问题；理解后再进入下一课。
7. 明确列出 `[自主阅读]` / `[自主实现]`：关联模块编号、阅读入口、可改范围、预期输出与验收；助手不默认替用户做完。

命名示例：`lesson-09: overfit a tiny batch with a minimal training loop`。教程、测试随课程交付，不集中拖到最后。使用 Git 历史查看课程当时的可运行状态，不为每课维护一份重复源码。

### 推荐仓库布局（逐课增加，不在 L00 一次铺完）

```text
llm-training-tutorial/
  AGENTS.md
  README.md
  pyproject.toml
  uv.lock
  openspec/
  .claude/plans/                 # 实施计划；引用正式 OpenSpec，避免两份任务状态
  docs/setup/README.md           # 目标训练机系统环境安装与复现说明
  docs/lessons/                  # 中文教程
  docs/extensions/index.md       # 自主阅读/实现模块索引，逐课补充，不是自动执行队列
  src/llm_tutorial/              # 渐进式主线代码；消息、推理后端、协议适配与工具运行时分层
  experiments/                  # 独立白盒实验
  configs/                      # tiny / learn 配置
  tests/fixtures/               # 小型、可公开的确定性样本
  data/                         # 真实语料，不提交
  runs/                         # 权重、日志和生成结果，不提交
```

## 7. 细化模块与用户自主扩展

### 标注与所有权

- `[主线]`：库优先的可运行基线，按批准的课程逐步实现。
- `[自主阅读]`：用户可沿阅读入口深入，助手提供问题清单，不默认展开长篇源码解读。
- `[自主实现]`：用户可独立完成的替代模块或实验，主线不依赖它；未经请求，助手不提前给完整实现。
- `[后续决策]`：会改变资源成本、兼容范围或训练目标，需要用户再次选择。

每个模块卡片包含：前置课程、主线边界、阅读入口、建议修改入口（创建时填写真实路径）、实验输入/输出、最小验收、难度和成本类别。自研替代实现放在独立实验入口，采用同一测试契约对照库实现，不破坏主线。

### 模块索引

完整 M01–M12 自主阅读/实现入口维护在 [docs/extensions/index.md](../../docs/extensions/index.md)。每课只展开相关模块，新增项目代码后填写真实入口；未经用户选择，不转为实施任务。

### 其他条件式扩展

- **蒸馏**：区分教师样本 SFT 与 logits 蒸馏；模型许可、API 费用或显存先批准。
- **thinking、多模态**：不是加标签即可获得的能力；新增数据、模板、协议字段和评测时独立规划。
- **MoE、DDP、多机训练**：Dense 单卡流程之后再考虑。
- **量化、GGUF、vLLM、WebUI**：在标准协议可用后按需求选；不因要求 API 调用就默认实施全部部署栈。
## 8. Review 决策与推进门槛

### 已确认

- 路线 A：库优先，核心机制用小实验解释。
- 路线覆盖模型使用、OpenAI/Anthropic 接口与 system/user 等消息角色；工具使用和后续强化训练纳入未来阶段。
- 每步一个提交，重要选择由用户决定。
- 自主阅读/实现模块显式标注，留给用户后续选择，不自动做完。
- 项目与首阶段已获 review；本机 Windows/5070 优先，Windows/5090 按性能瓶颈启用；安装文档必须落盘。

### 接下来依次确认

| 决策 | 建议 | 未确认前不做 |
|---|---|---|
| 升级到 5090（遇瓶颈时） | 用户在另一台 Windows 机器同步相同提交和锁文件，再验证 GPU | 不自动迁移、不改驱动、不安装 WSL、不推测性能 |
| 当前环境验收 | 本机 Windows/5070 与 CPU 分别实测并记录 | 不以 import、设备列表或退出码代替实际计算 |
| 协议边界 | 先 Chat Completions 与 Messages 的文本/流式，再加串行 tool use；两种都进入计划 | 不扩到完整厂商 API、不保证任意 Agent 客户端直接兼容 |
| 远端模型对照 | 官方 SDK 示例 + 默认关闭的远端调用 | 不读取未知凭据、不产生 API 费用、不把私人数据发出 |
| 再训练算法与目标 | 先用反馈定位问题，再由用户选 SFT/LoRA/DPO/GRPO | 不后台自我训练、不自动切换服务模型 |
| 数据/资源预算 | 微型 fixtures 优先，再根据实测确定规模 | 不全量下载、不长训、不产生云费用 |
| Git 远端 | 先本地逐课 commit，远端与 push 后续决定 | 不创建公开远端、不主动 push |

每课推进：用户确认继续 -> 说明目标与实验 -> 只实现该课 -> 执行验证 -> 一个提交 -> 展示 commit、结果、自检与扩展入口 -> 停下。遇到影响范围、成本、依赖路线或训练目标的选择时，先给选项，由用户决定。

L00 完成规划初始化，用户已 review；现在仅推进 L01 环境课，交付后停下等待下一课，不顺带实施模型、服务或正式训练。

## 9. 调研依据

本地证据：

- `D:\Github\minimind\README.md`：第 34–42 行的目标与耗时说明；482–514 行的数据与大小；584–645 行的模型与开销。
- `D:\Github\minimind\model\model_minimind.py`：模型配置、结构、loss shift、生成逻辑。
- `D:\Github\minimind\dataset\lm_dataset.py`：预训练/SFT/DPO 数据和标签。
- `D:\Github\minimind\trainer\train_pretrain.py`：主线训练循环与默认参数。
- `D:\Github\minimind\trainer\train_tokenizer.py`：第三方 BPE 实现与 tokenizer 复用提醒。
- `D:\Github\minimind\scripts\serve_openai_api.py`：已有 Chat Completions 端点、工具解析和 SSE，可作参考，不据此认定 Anthropic 已兼容。
- OpenSpec 1.16.0 本地 CLI help、`schemas/spec-driven/schema.yaml` 与 templates。
- 当前 `nvidia-smi`、Python/Torch 探针、WSL 发行版查询；这些不代表目标隔离环境已通过测试。

本轮实际查询的官方文档：

- [Transformers v4.57.6 Qwen3](https://github.com/huggingface/transformers/blob/v4.57.6/docs/source/en/model_doc/qwen3.md)
- [PEFT quicktour](https://github.com/huggingface/peft/blob/main/docs/source/quicktour.md)
- [TRL SFTTrainer：assistant-only loss 与模板要求](https://github.com/huggingface/trl/blob/main/docs/source/sft_trainer.md)
- [TRL DPOTrainer：偏好数据与训练](https://github.com/huggingface/trl/blob/main/docs/source/dpo_trainer.md)
- [OpenAI Python SDK](https://github.com/openai/openai-python/blob/main/README.md) 与 [tool message 类型](https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion_tool_message_param.py)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python/blob/main/README.md)、[Messages 请求类型](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_create_params.py) 与 [流事件类型](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/raw_message_stream_event.py)
- [TRL GRPOTrainer：reward、tools 与环境接口](https://github.com/huggingface/trl/blob/main/docs/source/grpo_trainer.md)

这些文档确认了候选能力与协议差异；main 分支会变，实施时必须锁定可验证版本。完整版本兼容、GPU 训练、SDK 接口集成和课程实验尚未执行。
