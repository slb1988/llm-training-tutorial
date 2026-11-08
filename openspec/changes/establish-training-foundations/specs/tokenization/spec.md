# Spec Delta

## Purpose

让学习者可以观察文本如何转换为模型输入，区分角色文本、序列边界与特殊标记，并独立练习训练分词器。主线词表有可追溯身份，实验产物不污染后续模型，从而支持跨课程和跨机器保持一致的数据解释。

## ADDED Requirements

### Requirement: Tokenizer behavior is inspectable
分词实验 SHALL 展示输入文本、token IDs、可读 token 与解码结果，说明规范化及特殊 token 保留规则，覆盖中文、英文和序列边界样例。

#### Scenario: Learner encodes and decodes a fixture
- **WHEN** 使用固定 tokenizer 对公开微型样例编解码
- **THEN** 解码结果符合声明的规范化策略，所有 ID 在词表范围内
- **AND** 角色字符串与真正特殊 token 的区别能够从输出检查

### Requirement: Main tokenizer identity is reproducible
主线 tokenizer SHALL 记录来源版本、资产哈希、词表大小与特殊 token 映射，能够在另一个 checkout 使用同一身份。

#### Scenario: Main assets are reloaded
- **WHEN** 在另一个进程加载相同 tokenizer 资产
- **THEN** 固定样例产生相同 token IDs，资产身份可以核对
- **AND** 不要求 MiniMind 存在于兄弟目录

### Requirement: Toy training does not replace main assets
分词训练实验 SHALL 从单独的训练样例生成隔离产物，保存后可重载；MUST NOT 覆盖主线 tokenizer 或使用验证/测试切分训练词表。

#### Scenario: Learner trains a toy tokenizer
- **WHEN** 对声明为训练用途的微型语料执行分词训练
- **THEN** 产物写到独立实验位置且重载后编解码一致，主线资产哈希保持不变

#### Scenario: No usable training text remains
- **WHEN** 输入为空或过滤后没有有效文本
- **THEN** 实验明确失败，不把没有学到有效合并的词表报告为训练完成
