# Spec Delta

## Purpose

让训练前的数据处理可追踪、可检查且能在微型样本上解释清楚，防止无效记录、数据泄漏或标签错位造成误导性的训练结果。准备好的输入与目标同时为后续模型训练和评估提供一致的基础，而不是仅输出一批无法核对的张量。

## ADDED Requirements

### Requirement: Corpus preparation exposes provenance and invalid records
语料处理 SHALL 保留文档来源/标识与处理配置，检查所需字段和非空文本，报告被拒绝记录及原因；默认只使用明确许可的公开或自写样例。

#### Scenario: A fixture contains invalid records
- **WHEN** 微型输入包含缺失文本或空记录
- **THEN** 可以定位无效记录与原因，并核对保留/拒绝数量
- **AND** 不将私人语料默认为训练来源

### Requirement: Dataset splits are deterministic and document-disjoint
数据准备 SHALL 在分块前完成精确去重与文档级 train/validation/test 切分；同一文档和精确重复文本 MUST NOT 跨切分，固定输入与 seed 应得到相同结果。

#### Scenario: A document would produce multiple chunks
- **WHEN** 对重复输入和长文档先切分再分块
- **THEN** 同源分块只出现在一个切分，精确重复文本不跨切分
- **AND** 重复运行能复现切分成员，清单记录使用的 seed

### Requirement: Next-token batches have inspectable target positions
batch 构造 SHALL 提供可核对的输入、目标与有效位置，保留有效结束标记且排除 padding 的 loss，确保 next-token 目标只对齐一次。

#### Scenario: Learner checks a hand-written token sequence
- **WHEN** 对带结束标记和 padding 的已知小序列构造 batch 并计算目标位置
- **THEN** 每个有效预测位置对应正确的下一个 token，padding 不参与 loss，结束标记未被误屏蔽
- **AND** 有效 token 数与手工预期一致

#### Scenario: No effective target exists
- **WHEN** 截断或输入长度导致没有有效预测目标
- **THEN** 提供明确错误或受控拒绝，不把空目标产生的非有限 loss 当作正常训练数据
