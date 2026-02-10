"""
ASB 原始代码快速测试 - 只测试初始化部分
"""

import os
import sys
from pathlib import Path

# 设置工作目录到 ASB_SOURCE_DATA
os.chdir(Path(__file__).parent / "ASB_SOURCE_DATA")
sys.path.insert(0, os.getcwd())

print("=" * 70)
print("ASB 原始代码 - 初始化测试")
print("=" * 70)
print(f"工作目录: {os.getcwd()}\n")

# 加载环境变量（从 safety-benchmarks/benchmarks/eval_benchmarks/asb/ 目录）
from dotenv import load_dotenv
env_path = Path(__file__).parent / "safety-benchmarks" / "benchmarks" / "eval_benchmarks" / "asb" / ".env"
print(f"加载环境变量: {env_path}")
load_dotenv(env_path)

# 检查 API 配置
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"\n[配置检查]")
print(f"API Key: {api_key[:20] if api_key else 'None'}...{api_key[-10:] if api_key else 'None'}")
print(f"Base URL: {base_url}")

if not api_key:
    print("\n❌ 错误: OPENAI_API_KEY 未设置")
    sys.exit(1)

print("\n✅ 环境变量加载成功")

# ==============================================================================
# 测试导入
# ==============================================================================

print("\n[测试导入原始 ASB 模块]")

try:
    from aios.llm_core import llms
    print("✓ 导入 aios.llm_core.llms")
except Exception as e:
    print(f"❌ 导入 aios.llm_core.llms 失败: {e}")
    sys.exit(1)

try:
    from aios.scheduler.fifo_scheduler import FIFOScheduler
    print("✓ 导入 aios.scheduler.fifo_scheduler")
except Exception as e:
    print(f"❌ 导入 aios.scheduler.fifo_scheduler 失败: {e}")
    sys.exit(1)

try:
    from pyopenagi.agents.agent_factory import AgentFactory
    print("✓ 导入 pyopenagi.agents.agent_factory")
except Exception as e:
    print(f"❌ 导入 pyopenagi.agents.agent_factory 失败: {e}")
    sys.exit(1)

try:
    from pyopenagi.agents.agent_process import AgentProcessFactory
    print("✓ 导入 pyopenagi.agents.agent_process")
except Exception as e:
    print(f"❌ 导入 pyopenagi.agents.agent_process 失败: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print("✓ 导入 pandas")
except Exception as e:
    print(f"❌ 导入 pandas 失败: {e}")
    sys.exit(1)

print("\n✅ 所有模块导入成功")

# ==============================================================================
# 测试加载数据
# ==============================================================================

print("\n[测试加载数据]")

try:
    tasks_path = "data/agent_task.jsonl"
    agent_tasks_df = pd.read_json(tasks_path, lines=True)
    print(f"✓ 加载 Agent 任务: {tasks_path}")
    print(f"  总 Agent 数: {len(agent_tasks_df)}")
except Exception as e:
    print(f"❌ 加载 Agent 任务失败: {e}")
    sys.exit(1)

try:
    attacker_tools_path = "data/all_attack_tools.jsonl"
    attacker_tools_df = pd.read_json(attacker_tools_path, lines=True)
    print(f"✓ 加载攻击工具: {attacker_tools_path}")
    print(f"  总攻击工具数: {len(attacker_tools_df)}")
except Exception as e:
    print(f"❌ 加载攻击工具失败: {e}")
    sys.exit(1)

# 选择测试数据
agent_info = agent_tasks_df.iloc[0]
agent_name = agent_info["agent_name"]
task = agent_info["tasks"][0]
attacker_tools = attacker_tools_df[attacker_tools_df["Corresponding Agent"] == agent_name]
attacker_tool = attacker_tools.iloc[0]

print(f"\n[选择的测试数据]")
print(f"Agent: {agent_name}")
print(f"任务: {task}")
print(f"攻击工具: {attacker_tool['Attacker Tool']}")
print(f"攻击目标: {attacker_tool['Attack goal']}")

print("\n" + "=" * 70)
print("✅ 初始化测试完成！")
print("=" * 70)
