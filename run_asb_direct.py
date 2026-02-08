"""
ASB 直接测试脚本（绕过其他 benchmark 的依赖）

直接导入和测试 ASB
"""

import os
import sys
from pathlib import Path

# 设置路径
asb_dir = Path(__file__).parent / "safety-benchmarks/benchmarks/eval_benchmarks/asb"
sys.path.insert(0, str(asb_dir))

# 加载环境变量
from dotenv import load_dotenv
env_path = asb_dir / ".env"
load_dotenv(env_path)

print("=" * 70)
print("ASB DPI 攻击 - 直接测试")
print("=" * 70)

# 检查 API 配置
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"\nAPI Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
print(f"Base URL: {base_url}")

# 直接导入 ASB 模块
print(f"\n导入 ASB 模块...")

try:
    from dataset import load_asb_dataset
    print(f"  [OK] dataset imported")

    from solver import asb_react_solver
    print(f"  [OK] solver imported")

    from scorer import asr_scorer, tsr_scorer, rr_scorer
    print(f"  [OK] scorer imported")

    # 导入 inspect_ai 组件
    from inspect_ai import task, Task, GenerateConfig
    print(f"  [OK] inspect_ai imported")

except Exception as e:
    print(f"  [FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 创建 Task
print(f"\n创建 Task...")

try:
    # 加载数据集
    dataset = load_asb_dataset(
        agent_names=["financial_analyst_agent"],
        attack_types=["dpi"],
        limit=1,
        shuffle=False
    )

    print(f"  数据集大小: {len(dataset)}")

    # 显示样本信息
    if len(dataset) > 0:
        sample = dataset.samples[0]
        print(f"\n  第一个样本:")
        print(f"    ID: {sample.id}")
        print(f"    Input: {sample.input[:100]}...")

        # 选择攻击工具
        attack_tools = sample.metadata.get('available_attack_tools', [])
        if attack_tools:
            import random
            selected_tool = random.choice(attack_tools)
            attacker_goal = selected_tool['attack_goal']
            sample.metadata['attacker_goal'] = attacker_goal

            print(f"\n  攻击工具:")
            print(f"    名称: {selected_tool['tool_name']}")
            print(f"    目标: {attacker_goal[:80]}...")

    # 定义 Task
    @task
    def test_task():
        return Task(
            dataset=dataset,
            solver=[asb_react_solver(attack_type="dpi", temperature=0.0)],
            scorer=[asr_scorer(), tsr_scorer()],
            config=GenerateConfig(temperature=0.0, max_tokens=256)
        )

    print(f"\n  Task 创建成功")

except Exception as e:
    print(f"  [FAIL] Task 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 运行评测
print(f"\n运行评测...")
from inspect_ai import eval

try:
    results = eval(
        test_task(),
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
                print(f"\n  {scorer_name.upper()}:")
                print(f"    分数: {score.value:.4f}")
                print(f"    说明: {score.explanation}")

        # 显示最后响应
        if hasattr(result, 'messages') and result.messages:
            assistant_msgs = [m for m in result.messages if hasattr(m, 'role') and m.role == 'assistant']
            if assistant_msgs:
                last_msg = assistant_msgs[-1]
                content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                print(f"\n最后响应 ({len(content)} 字符):")
                print(content[:500] + "..." if len(content) > 500 else content)

    print(f"\n" + "=" * 70)
    print(f"测试完成！")
    print(f"=" * 70)

except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
