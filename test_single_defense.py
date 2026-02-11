#!/usr/bin/env python3
"""
测试单个防御策略实现
"""
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "safety-benchmarks" / "benchmarks"))

from dotenv import load_dotenv
from inspect_ai import eval
from eval_benchmarks.asb import asb

# 加载环境
load_dotenv(Path(__file__).parent / "safety-benchmarks" / "benchmarks" / "eval_benchmarks" / "asb" / ".env")


print("=" * 80)
print(" 测试 delimiters_defense")
print("=" * 80)

task = asb(
    agent_names=["system_admin_agent"],
    attack_type="dpi",
    limit=1,
    shuffle=False,
    defense_type="delimiters_defense"
)

results = eval(
    task,
    model="openai/deepseek-v3.2",
    log_level="info"
)

print("\n" + "=" * 80)
print(" 测试完成")
print("=" * 80)
