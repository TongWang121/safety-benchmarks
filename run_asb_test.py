"""
ASB 单样本快速测试

测试 DPI 攻击的第一个样本
"""

import os
import sys
from pathlib import Path

# 设置路径
benchmarks_dir = Path(__file__).parent / "safety-benchmarks"
os.chdir(benchmarks_dir)
sys.path.insert(0, str(benchmarks_dir / "benchmarks"))

# 加载环境变量
from dotenv import load_dotenv
env_path = benchmarks_dir / "benchmarks/eval_benchmarks/asb/.env"
load_dotenv(env_path)

print("=" * 70)
print("ASB DPI 攻击 - 单样本测试")
print("=" * 70)

# 检查 API 配置
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"\nAPI Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
print(f"Base URL: {base_url}")

# 导入并创建 Task
print(f"\n创建 Task...")
from eval_benchmarks.asb import asb

task = asb(
    agent_names=["financial_analyst_agent"],
    attack_type="dpi",
    limit=1,
    shuffle=False
)

print(f"数据集大小: {len(task.dataset)}")

# 显示样本信息
if len(task.dataset) > 0:
    sample = task.dataset.samples[0]
    print(f"\n第一个样本:")
    print(f"  ID: {sample.id}")
    print(f"  Input: {sample.input}")

    attack_tools = sample.metadata.get('available_attack_tools', [])
    if attack_tools:
        import random
        selected_tool = random.choice(attack_tools)
        sample.metadata['attacker_goal'] = selected_tool['attack_goal']
        print(f"\n攻击工具: {selected_tool['tool_name']}")
        print(f"攻击目标: {selected_tool['attack_goal']}")

# 运行评测
print(f"\n运行评测...")
from inspect_ai import eval

try:
    results = eval(
        task,
        model="openai/gpt-4o-mini",
        model_args={
            "api_key": api_key,
            "base_url": base_url,
        },
        log_limit=5
    )

    # 显示结果
    print(f"\n" + "=" * 70)
    print(f"评测结果")
    print(f"=" * 70)

    if results and len(results) > 0:
        result = results[0]
        print(f"\n样本 ID: {result.sample_id}")
        print(f"状态: {result.status}")

        if hasattr(result, 'scores') and result.scores:
            print(f"\n评分结果:")
            for scorer_name, score in result.scores.items():
                print(f"\n  {scorer_name.upper()}: {score.value:.4f}")
                print(f"    说明: {score.explanation}")

    print(f"\n测试完成！")

except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
