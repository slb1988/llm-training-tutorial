# Spec Delta

## Purpose

让学习者能按小步骤理解语言模型训练的输入、计算和结果，每课都有可以复现的实验与证据，并能够回到对应提交继续学习。自主阅读与替代实现保持独立，避免一次性交付完整工程而失去学习过程。

## ADDED Requirements

### Requirement: Each lesson has a reproducible learning unit
每个实现课 SHALL 提供中文目标、前置知识、运行命令、预期观察、失败判定、自检问题和对应验证，说明实验解决什么问题及不能证明什么。

#### Scenario: Learner follows a completed lesson
- **WHEN** 学习者 checkout 该课提交并使用文档声明的环境运行示例
- **THEN** 可以获得文档说明的观察结果并执行该课验证
- **AND** 文档将机制验证与真实模型能力区分，不将示例成功等同于泛化能力

### Requirement: Lesson progress matches one verified commit
每课 SHALL 将本课实现、测试、教程和任务完成状态放在一个可定位的提交中；未完成验证或仅存在规划文档时 MUST NOT 标为实现完成。

#### Scenario: Lesson passes its acceptance checks
- **WHEN** 获准的一课完成且本课验收有证据
- **THEN** 一个带课程编号的提交包含该课交付，任务状态与证据一致
- **AND** 执行在该课后停止，不自动推进下一课

#### Scenario: Target verification is missing
- **WHEN** 该课要求目标 GPU 验证但尚未获得结果
- **THEN** 课程状态保持未完成并说明缺失证据，不用其他机器结果代替

### Requirement: Planning review precedes lesson implementation
课程实施 SHALL 等待用户 review 和指定步骤授权；规划格式检查通过或文档齐全 MUST NOT 被视为实施授权。

#### Scenario: Planning artifacts are complete
- **WHEN** 首阶段 proposal、specs、design 和 tasks 均已创建
- **THEN** 交付供用户 review，不自动开始安装依赖或执行 L01

### Requirement: Independent extensions remain optional
教程 SHALL 标注自主阅读、实现范围、前置课程与最小验收；主线 MUST 在未完成自主练习时仍可运行。

#### Scenario: Learner selects an extension later
- **WHEN** 用户此前尚未选择某个自主实现模块
- **THEN** 它保留为独立学习入口，不被自动实现或计为当前阶段未完成任务
