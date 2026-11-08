# Spec Delta

## Purpose

为学习者提供可解释的小型语言模型计算与训练起点，使随机权重、模型输入输出、梯度和因果约束都能在有限成本下验证。本阶段建立基础计算契约，后续课程再扩展训练循环和质量评估，避免把初始化成功误当作已经训练出语言能力。

## ADDED Requirements

### Requirement: Gradient experiments can be checked independently
梯度实验 SHALL 使用可手工验证的小规模函数，展示解析梯度与自动微分的比较，以及一次受控参数更新对目标值的影响。

#### Scenario: Learner runs the gradient fixture
- **WHEN** 使用固定输入和明确学习率执行小实验
- **THEN** 自动梯度与解析梯度在声明容差内一致，参数确实变化，目标值按实验预期下降
- **AND** 输出说明这不是语言模型的泛化验收

### Requirement: Causal attention cannot observe future input
注意力实验 SHALL 展示张量形状与因果限制；在关闭随机扰动的条件下，修改未来位置输入 MUST NOT 改变此前位置的输出。

#### Scenario: Future tokens are perturbed
- **WHEN** 对固定序列仅改变某个位置之后的输入
- **THEN** 此前输出在声明数值容差内保持一致，可以检查因果遮罩对应的可见范围

### Requirement: Small models initialize without pretrained weights
小模型实验 SHALL 从声明配置与随机 seed 初始化权重，报告参数量与 tokenizer 身份；MUST NOT 加载现成模型权重冒充从零初始化。

#### Scenario: Learner initializes a tiny model offline
- **WHEN** 所需配置和 tokenizer 资产已准备好且网络不可用
- **THEN** 无须获取预训练权重即可创建模型并报告参数量
- **AND** 同一受支持 CPU 环境和 seed 的初始化可复现

### Requirement: Forward outputs match the token contract
模型前向 SHALL 对 batch 输出与词表一致的预测分数及有限 loss；词表、特殊 token 与输入范围不相容时 MUST 明确拒绝。

#### Scenario: Valid token batch is evaluated
- **WHEN** 使用声明词表范围内的带有效目标的 batch
- **THEN** 输出形状为 batch 大小乘序列长度乘词表大小，loss 为有限值且 next-token 对齐与数据契约一致

#### Scenario: Tokenizer and model disagree
- **WHEN** 输入 token ID 或特殊 token 映射不符合模型声明
- **THEN** 实验给出可定位错误，不静默换 tokenizer、截断词表或加载其他模型
