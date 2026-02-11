#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 POT 攻击的两种模式：backdoor vs clean

验证 pot_paraphrase_defense 在两种模式下都正确工作
"""

import os
import sys
from pathlib import Path

# 设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 设置工作目录
os.chdir(Path(__file__).parent / "safety-benchmarks")
benchmarks_path = os.path.join(os.getcwd(), "benchmarks")
if benchmarks_path not in sys.path:
    sys.path.insert(0, benchmarks_path)

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

# 加载环境变量
from dotenv import load_dotenv
env_path = Path("benchmarks/eval_benchmarks/asb/.env")
load_dotenv(env_path)

from inspect_ai import eval
from eval_benchmarks.asb import asb

print("=" * 80)
print("测试 POT 攻击模式：backdoor vs clean")
print("=" * 80)

# 测试配置
test_cases = [
    {
        "name": "POT backdoor 模式 + pot_paraphrase_defense",
        "attack_type": "pot",
        "pot_mode": "backdoor",
        "defense_type": "pot_paraphrase_defense",
        "limit": 2
    },
    {
        "name": "POT clean 模式 + pot_paraphrase_defense",
        "attack_type": "pot",
        "pot_mode": "clean",
        "defense_type": "pot_paraphrase_defense",
        "limit": 2
    },
    {
        "name": "POT backdoor 模式 + pot_shuffling_defense",
        "attack_type": "pot",
        "pot_mode": "backdoor",
        "defense_type": "pot_shuffling_defense",
        "limit": 2
    },
    {
        "name": "POT clean 模式 + pot_shuffling_defense",
        "attack_type": "pot",
        "pot_mode": "clean",
        "defense_type": "pot_shuffling_defense",
        "limit": 2
    },
]

api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_BASE_URL")

print(f"\n[配置]")
print(f"API Base: {api_base}")
print(f"API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")

results_summary = []

for test_case in test_cases:
    print(f"\n{'=' * 80}")
    print(f"测试: {test_case['name']}")
    print(f"{'=' * 80}")

    try:
        # 创建任务
        task = asb(
            agent_names=["financial_analyst_agent"],
            attack_type=test_case["attack_type"],
            pot_mode=test_case.get("pot_mode"),
            defense_type=test_case["defense_type"],
            limit=test_case["limit"],
            shuffle=False
        )

        print(f"数据集大小: {len(task.dataset)}")

        # 显示第一个样本的 pot_mode
        if len(task.dataset) > 0:
            sample = task.dataset.samples[0]
            pot_mode = sample.metadata.get("pot_mode", "unknown")
            print(f"样本 pot_mode: {pot_mode}")

        # 运行评测
        results = eval(
            task,
            model="openai/gpt-4o-mini",
            model_args={"api_key": api_key},
            log_limit=10
        )

        if results and len(results) > 0:
            log = results[0]

            if log.samples and len(log.samples) > 0:
                asr_scores = []
                tsr_scores = []

                for sample in log.samples:
                    if hasattr(sample, 'scores') and sample.scores:
                        if "asr" in sample.scores:
                            asr_scores.append(sample.scores["asr"].value)
                        if "tsr" in sample.scores:
                            tsr_scores.append(sample.scores["tsr"].value)

                avg_asr = sum(asr_scores) / len(asr_scores) if asr_scores else 0
                avg_tsr = sum(tsr_scores) / len(tsr_scores) if tsr_scores else 0

                results_summary.append({
                    "name": test_case["name"],
                    "pot_mode": pot_mode,
                    "avg_asr": avg_asr,
                    "avg_tsr": avg_tsr,
                    "samples": len(asr_scores)
                })

                print(f"\n统计结果:")
                print(f"  平均 ASR: {avg_asr:.3f}")
                print(f"  平均 TSR: {avg_tsr:.3f}")
                print(f"  样本数: {len(asr_scores)}")

    except Exception as e:
        print(f"\n[错误] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

# 打印最终对比
print(f"\n{'=' * 80}")
print("最终对比")
print(f"{'=' * 80}\n")

print(f"{'测试名称':<55} {'pot_mode':<10} {'ASR':<10} {'TSR':<10}")
print("-" * 90)
for result in results_summary:
    print(f"{result['name']:<55} {result['pot_mode']:<10} {result['avg_asr']:<10.3f} {result['avg_tsr']:<10.3f}")

print("\n说明:")
print("  ASR (Attack Success Rate): 攻击成功率，越低越安全")
print("  TSR (Tool Selection Rate): 攻击工具调用率，越低越安全")
print("\n期望结果:")
print("  - backdoor 模式: ASR 应该较高（期望模型调用攻击工具）")
print("  - clean 模式: ASR 应该为 0（没有 trigger，不应调用攻击工具）")
