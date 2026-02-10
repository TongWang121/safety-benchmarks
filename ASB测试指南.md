# ASB 测试环境设置指南

## 目的

使用 ASB_SOURCE_DATA/data/ 目录下的原始测试数据集，验证修复后的代码是否与原始代码的消息流一致。

## 步骤

### 1. 设置测试环境

首先运行设置脚本，将测试数据复制到框架数据目录：

```bash
cd e:\code\aisafety\ASB1
python setup_asb_test_env.py
```

这个脚本会：
- 复制 `agent_task_test.jsonl` 到 `safety-benchmarks/benchmarks/eval_benchmarks/asb/data/`
- 复制 `attack_tools_test.jsonl` 到相同目录
- 备份原始的 `dataset.py` 并修改以使用测试数据集

### 2. 运行测试

```bash
python test_asb_original_data.py
```

### 3. 恢复原始数据集（可选）

测试完成后，可以恢复使用完整数据集：

```bash
python restore_asb_dataset.py
```

## 预期结果

### 成功的情况

如果你看到的输出中 **Step 2 包含 `[Thinking]:` 前缀**，说明修复成功：

```
[DEBUG] ===== Step 2/2 =====
[DEBUG] tool_use: []  # ← 空数组
[DEBUG] Response: [Action]: I will call the TransactionDuplication...;[Observation]: ...
[DEBUG] LLM returned complete Action+Observation format (including [Thinking]:)

然后消息历史中应该包含：
[Thinking]: [Action]: I will call the TransactionDuplication...;[Observation]: ...
```

### 不成功的情况

如果 Step 2 的 `tool_use` 不是 `[]`（例如 `['TransactionDuplication']`），则：
- LLM 会返回标准格式的工具调用
- **不会**有 `[Thinking]:` 前缀
- 这是正确的行为，因为原始代码在相同条件下也是如此

## 故障排除

### 问题 1：导入错误

如果看到 `无法解析导入"eval_benchmarks.asb"` 的警告：
- 这是 IDE 的警告，不影响实际运行
- 可以忽略

### 问题 2：测试文件不存在

如果提示 `测试环境未设置`：
- 确保已运行 `setup_asb_test_env.py`
- 检查 `ASB_SOURCE_DATA/data/` 目录下是否存在测试文件

### 问题 3：LLM 返回格式不同

如果 LLM 返回的消息格式与预期不同：
- 这是正常的，因为 LLM 的响应是随机的
- 多运行几次测试，或者增加样本数量

## 相关文件

- `setup_asb_test_env.py` - 设置测试环境
- `test_asb_original_data.py` - 运行测试
- `restore_asb_dataset.py` - 恢复原始数据集
- `safety-benchmarks/benchmarks/eval_benchmarks/asb/solver.py` - 修复后的代码

## 修改摘要

### solver.py 的修改

1. **添加完整 Action+Observation 格式检测**（第 469-475 行）
   - 检测 LLM 是否返回完整的 `[Action]:...;[Observation]:...` 格式
   - 如果是，直接使用原始响应（保留 `[Thinking]:` 前缀）

2. **修正 attacker_tool_injection 调用条件**（第 363-367 行）
   - 只在 DPI 或 OPI 攻击时注入攻击工具
   - 与原始代码逻辑一致
