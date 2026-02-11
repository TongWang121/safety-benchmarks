#!/usr/bin/env python3
"""
测试防御策略实现
"""

import sys
import os
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "safety-benchmarks" / "benchmarks"))

from dotenv import load_dotenv
from inspect_ai import eval
from eval_benchmarks.asb import asb

# 加载环境
load_dotenv(Path(__file__).parent / "safety-benchmarks" / "benchmarks" / "eval_benchmarks" / "asb" / ".env")

print("=" * 80)
print(" ASB 防御策略测试")
print("=" * 80)

# 定义测试配置
test_configs = [
    {
        "name": "delimiters_defense",
        "attack_type": "dpi",
        "defense_type": "delimiters_defense",
        "description": "用 <start> 和 <end> 包装任务"
    },
    {
        "name": "instructional_prevention",
        "attack_type": "dpi",
        "defense_type": "instructional_prevention",
        "description": "警告恶意用户可能改变指令"
    },
    {
        "name": "direct_paraphrase_defense",
        "attack_type": "dpi",
        "defense_type": "direct_paraphrase_defense",
        "description": "改写任务以避免触发器"
    },
    {
        "name": "dynamic_prompt_rewriting",
        "attack_type": "dpi",
        "defense_type": "dynamic_prompt_rewriting",
        "description": "动态重写任务以增强安全性"
    },
    {
        "name": "ob_sandwich_defense",
        "attack_type": "opi",
        "defense_type": "ob_sandwich_defense",
        "description": "在工具结果中添加提醒"
    },
    {
        "name": "pot_paraphrase_defense",
        "attack_type": "pot",
        "defense_type": "pot_paraphrase_defense",
        "description": "改写 PoT 任务以避免触发器"
    },
    {
        "name": "pot_shuffling_defense",
        "attack_type": "pot",
        "defense_type": "pot_shuffling_defense",
        "description": "打乱 PoT 示例顺序"
    },
]

# 选择要测试的防御策略
# 可以通过修改索引选择，例如 test_configs[0:1] 只测试第一个
selected_tests = test_configs  # 测试所有防御策略

print(f"\n将测试 {len(selected_tests)} 个防御策略：")
for i, config in enumerate(selected_tests, 1):
    print(f"  {i}. {config['name']}: {config['description']}")

# 循环测试每个防御策略
for i, config in enumerate(selected_tests, 1):
    print("\n" + "=" * 80)
    print(f" {i}/{len(selected_tests)} - 测试 {config['name']}")
    print(f" 攻击类型: {config['attack_type']} | 防御类型: {config['defense_type']}")
    print(f" 描述: {config['description']}")
    print("-" * 80)

    try:
        task = asb(
            agent_names=["system_admin_agent"],
            attack_type=config["attack_type"],
            limit=1,
            shuffle=False,
            defense_type=config["defense_type"]
        )

        results = eval(
            task,
            model="openai/deepseek-v3.2",
            log_level="warning"  # 减少日志输出
        )

        if results:
            print(f"\n结果:")
            print(f"  ASR: {results[0].metrics['asr_metric'].value}")
            print(f"  TSR: {results[0].metrics['tsr_metric'].value}")
            print(f"  RR: {results[0].metrics['rr_metric'].value}")
            print(f"  日志: {results[0].log_path}")
        else:
            print(f"\n未返回结果")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print(" 所有测试完成")
print("=" * 80)
