#!/usr/bin/env python3
"""
简化的 MP 攻击测试脚本 - 验证导入和配置
"""

import sys
import os
from pathlib import Path

# 设置路径
project_root = os.path.dirname(__file__)
benchmarks_path = os.path.join(project_root, "safety-benchmarks", "benchmarks")
sys.path.insert(0, benchmarks_path)

print("=" * 60)
print(" MP 攻击测试 - 配置验证")
print("=" * 60)
print(f"项目根目录: {project_root}")
print(f"Benchmarks 路径: {benchmarks_path}")
print(f"路径存在: {os.path.exists(benchmarks_path)}")

# 测试导入
print("\n[1] 测试导入...")
try:
    from eval_benchmarks.asb.dataset import load_asb_dataset
    from eval_benchmarks.asb.solver import asb_react_solver
    from eval_benchmarks.asb.scorer import asr_scorer, tsr_scorer, rr_scorer
    from eval_benchmarks.asb.tools import SimulatedToolRegistry
    print("✅ 所有导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 测试数据目录
print("\n[2] 测试数据目录...")
data_dir = Path(project_root) / "safety-benchmarks/benchmarks/eval_benchmarks/asb/data"
print(f"数据目录: {data_dir}")
print(f"目录存在: {data_dir.exists()}")

if data_dir.exists():
    files = list(data_dir.glob("*.jsonl"))
    print(f"✅ 找到 {len(files)} 个 JSONL 文件:")
    for f in files:
        print(f"  - {f.name}")

# 测试数据集加载
print("\n[3] 测试数据集加载...")
try:
    dataset = load_asb_dataset(
        agent_names=["system_admin_agent"],
        attack_types=["mp"],
        limit=1,
        shuffle=False
    )
    print(f"✅ 数据集加载成功: {len(dataset)} 个样本")
    if dataset:
        print(f"  样本 ID: {dataset[0].id}")
        print(f"  任务: {dataset[0].input[:80]}...")
except Exception as e:
    print(f"❌ 数据集加载失败: {e}")
    import traceback
    traceback.print_exc()

# 测试工具注册表
print("\n[4] 测试工具注册表...")
try:
    registry = SimulatedToolRegistry(data_dir=data_dir)
    tools = registry.get_all_tools_for_agent("system_admin_agent")
    print(f"✅ 工具加载成功: {len(tools)} 个工具")
    for tool_name in tools:
        print(f"  - {tool_name}")
except Exception as e:
    print(f"❌ 工具加载失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print(" 验证完成")
print("=" * 60)
