#!/usr/bin/env python3
"""
测试防御策略 - 简化版本，只输出结果摘要
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "safety-benchmarks" / "benchmarks"))

from dotenv import load_dotenv
from inspect_ai import eval
from eval_benchmarks.asb import asb

load_dotenv(Path(__file__).parent / "safety-benchmarks" / "benchmarks" / "eval_benchmarks" / "asb" / ".env")

print("=" * 60)
print(" ASB 防御策略快速测试")
print("=" * 60)

test_configs = [
    ("delimiters_defense", "dpi", "delimiters_defense"),
    ("instructional_prevention", "dpi", "instructional_prevention"),
    ("direct_paraphrase_defense", "dpi", "direct_paraphrase_defense"),
    ("dynamic_prompt_rewriting", "dpi", "dynamic_prompt_rewriting"),
    ("ob_sandwich_defense", "opi", "ob_sandwich_defense"),
    ("pot_paraphrase_defense", "pot", "pot_paraphrase_defense"),
    ("pot_shuffling_defense", "pot", "pot_shuffling_defense"),
]

results_summary = []

for name, attack_type, defense_type in test_configs:
    print(f"\n测试: {name}...", end=" ", flush=True)
    try:
        task = asb(
            agent_names=["system_admin_agent"],
            attack_type=attack_type,
            limit=1,
            shuffle=False,
            defense_type=defense_type
        )

        result = eval(
            task,
            model="openai/deepseek-v3.2",
            log_level="error"  # 最小化日志
        )

        if result:
            asr = result[0].metrics['asr_metric'].value
            tsr = result[0].metrics['tsr_metric'].value
            rr = result[0].metrics['rr_metric'].value
            results_summary.append((name, asr, tsr, rr))
            print(f"ASR={asr:.3f} TSR={tsr:.3f} RR={rr:.3f}")
        else:
            print("失败")
    except Exception as e:
        print(f"错误: {e}")

print("\n" + "=" * 60)
print(" 结果汇总")
print("=" * 60)
print(f"{'防御策略':<30} {'ASR':<8} {'TSR':<8} {'RR':<8}")
print("-" * 60)
for name, asr, tsr, rr in results_summary:
    print(f"{name:<30} {asr:<8.3f} {tsr:<8.3f} {rr:<8.3f}")
print("=" * 60)
