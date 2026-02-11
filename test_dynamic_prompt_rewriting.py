#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 dynamic_prompt_rewriting 防御修复

验证：
1. 攻击在防御之前注入（源代码逻辑）
2. 防御处理的是包含攻击的完整输入
3. 恶意指令被成功移除
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
print("测试 dynamic_prompt_rewriting 防御")
print("=" * 80)

# 测试配置
test_cases = [
    {
        "name": "DPI 攻击 + dynamic_prompt_rewriting 防御",
        "attack_type": "dpi",
        "defense_type": "dynamic_prompt_rewriting",
        "limit": 3
    },
    {
        "name": "DPI 攻击 + direct_paraphrase_defense 防御",
        "attack_type": "dpi",
        "defense_type": "direct_paraphrase_defense",
        "limit": 3
    },
    {
        "name": "DPI 攻击 + 无防御（对照组）",
        "attack_type": "dpi",
        "defense_type": None,
        "limit": 3
    }
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

    # 创建任务
    task = asb(
        agent_names=["financial_analyst_agent"],
        attack_type=test_case["attack_type"],
        defense_type=test_case["defense_type"],
        limit=test_case["limit"],
        shuffle=False
    )

    print(f"数据集大小: {len(task.dataset)}")

    try:
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
                # 统计结果
                asr_scores = []
                tsr_scores = []

                for sample in log.samples:
                    if hasattr(sample, 'scores') and sample.scores:
                        if "asr" in sample.scores:
                            asr_scores.append(sample.scores["asr"].value)
                        if "tsr" in sample.scores:
                            tsr_scores.append(sample.scores["tsr"].value)

                        # 打印样本详情
                        print(f"\n样本 {sample.id}:")
                        if "asr" in sample.scores:
                            print(f"  ASR: {sample.scores['asr'].value:.3f} - {sample.scores['asr'].explanation}")
                        if "tsr" in sample.scores:
                            print(f"  TSR: {sample.scores['tsr'].value:.3f} - {sample.scores['tsr'].explanation}")

                # 计算平均值
                avg_asr = sum(asr_scores) / len(asr_scores) if asr_scores else 0
                avg_tsr = sum(tsr_scores) / len(tsr_scores) if tsr_scores else 0

                results_summary.append({
                    "name": test_case["name"],
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

print(f"{'测试名称':<50} {'ASR':<10} {'TSR':<10}")
print("-" * 80)
for result in results_summary:
    print(f"{result['name']:<50} {result['avg_asr']:<10.3f} {result['avg_tsr']:<10.3f}")

print("\n说明:")
print("  ASR (Attack Success Rate): 攻击成功率，越低越安全")
print("  TSR (Tool Selection Rate): 攻击工具调用率，越低越安全")
print("\n期望结果:")
print("  - dynamic_prompt_rewriting 的 ASR 应显著低于无防御")
print("  - direct_paraphrase_defense 的 ASR 应显著低于无防御")
