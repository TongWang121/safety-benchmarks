#!/usr/bin/env python3
"""
验证消息顺序 - 确认与源代码一致
"""

import asyncio
import os
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
print(" 验证消息顺序 - MP 攻击")
print("=" * 80)

# 创建任务
task = asb(
    agent_names=["system_admin_agent"],
    attack_type="mp",
    limit=1,
    shuffle=False
)

print(f"\n任务创建成功")
print(f"  数据集大小: {len(task.dataset)}")

# 修改 solver 以添加调试输出
from eval_benchmarks.asb.solver import asb_react_solver

async def run_with_debug():
    # 手动调用 solver 来观察消息顺序
    from inspect_ai import TaskState
    from inspect_ai.model import ChatMessageUser, ChatMessageSystem, ChatMessageAssistant

    # 创建模拟的 TaskState
    sample = task.dataset.samples[0]

    # 创建一个简单的 runner 来捕获消息
    original_solve = asb_react_solver(max_iterations=10, temperature=0.0, attack_type="mp").solve

    async def debug_solve(state, generate):
        # 添加调试钩子
        print("\n" + "=" * 80)
        print(" 消息顺序跟踪")
        print("=" * 80)

        # 在关键位置打印消息
        step = 0

        async def track_generate(state):
            nonlocal step
            print(f"\n[Generate Call #{step+1}]")
            print(f"  当前消息数: {len(state.messages)}")
            for i, msg in enumerate(state.messages):
                role = msg.role
                content = msg.content if hasattr(msg, 'content') else str(msg)[:100]
                print(f"    [{i+1}] {role}: {content if len(content) <= 100 else content[:100]+'...'}")
            step += 1
            return await generate(state)

        result = await original_solve(state, track_generate)
        return result

    # 运行评估
    results = await eval(
        task,
        model="openai/deepseek-v3.2",
        log_level="info"
    )

    return results

if __name__ == "__main__":
    results = asyncio.run(run_with_debug())

    print("\n" + "=" * 80)
    print(" 测试完成")
    print("=" * 80)
