# Spec Delta

## Purpose

让学习者能在独立的真实训练机器上安装和重建项目环境，并理解系统驱动、训练运行时与项目依赖之间的边界。环境文档与设备验证共同提供证据，避免把编写机器的状态误当成另一台训练电脑已经可以运行。

## ADDED Requirements

### Requirement: Installation instructions are durable and target-specific
项目 SHALL 在仓库中维护系统环境安装说明，覆盖已选 OS 的前置条件、隔离依赖安装、重建、验证与常见问题；未确认或未验证的步骤 MUST 明确标注状态。

#### Scenario: Secondary machine is not yet verified
- **WHEN** 本机 Windows/5070 是当前开发与验证目标，而另一台 Windows/5090 尚未运行探针
- **THEN** 文档提供本机安装路径并保留 5090 的迁移检查，不宣称后者已经验证或阻塞本机课程

#### Scenario: Learner recreates the selected environment
- **WHEN** 用户按目标平台说明在新的项目隔离环境中安装
- **THEN** 能得到已记录的兼容依赖组合，并运行文档中的 CPU 和 GPU 验证
- **AND** 依赖变化时安装文档随对应课程更新，而非只在聊天中给命令

### Requirement: Device checks prove actual computation
设备验证 SHALL 报告实际硬件与运行时信息，并执行有限值的前向、反向和参数更新；请求 GPU 时 MUST NOT 静默回退到 CPU。

#### Scenario: CUDA computation succeeds on the target
- **WHEN** 在当前选定的本机 5070 上运行 GPU 探针，或迁移后在 5090 上重新运行
- **THEN** 输出实际设备、运行时版本、同步完成的计算结果和通过判定

#### Scenario: Requested GPU runtime is unavailable
- **WHEN** 用户请求 GPU 但环境只有 CPU 运行时或 GPU 计算失败
- **THEN** 探针明确失败并提供定位信息，而不输出 GPU 验证成功

### Requirement: CPU and target GPU evidence remain distinct
验收记录 SHALL 分开标识 CPU、本机 5070、后备 5090 与模型能力证据，记录命令、Git revision、环境版本及结果；当前课程可由选定的本机 CPU/GPU 验收完成。

#### Scenario: Only the authoring machine was tested
- **WHEN** 本机 CPU/5070 验证通过，但尚未在用户 5090 机器获得运行证据
- **THEN** L01 可按本机验收完成，5090 仍标为未验证，不能由本机设备或退出码推断迁移成功

### Requirement: Environment setup preserves machine boundaries
环境操作 SHALL 使用项目隔离依赖和可迁移的 checkout 路径；系统驱动、OS、远程机器或全局环境变更 MUST 另获用户批准。

#### Scenario: A driver change is required
- **WHEN** 探针发现目标驱动与候选运行时不兼容
- **THEN** 报告需要的选择并暂停，不自动更改驱动或安装新的操作系统
