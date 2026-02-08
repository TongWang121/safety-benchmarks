"""调试工具传递"""
import os
import sys
from pathlib import Path

# 设置环境
os.chdir(Path(__file__).parent / "safety-benchmarks")
benchmarks_path = os.path.join(os.getcwd(), "benchmarks")
if benchmarks_path not in sys.path:
    sys.path.insert(0, benchmarks_path)

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
env_path = Path("benchmarks/eval_benchmarks/asb/.env")
load_dotenv(env_path)

from eval_benchmarks.asb import asb

# 创建 Task
task = asb(
    agent_names=["financial_analyst_agent"],
    attack_type="dpi",
    limit=1,
    shuffle=False
)

print(f"=== Task Info ===")
print(f"Dataset size: {len(task.dataset)}")
print(f"Tools: {len(task.tools) if task.tools else 0}")

if task.tools:
    print(f"\n=== First 5 Tools ===")
    for i, tool in enumerate(task.tools[:5]):
        print(f"\nTool {i}:")
        print(f"  Type: {type(tool)}")
        print(f"  Name: {tool.name if hasattr(tool, 'name') else getattr(tool, '__name__', 'unknown')}")
        if hasattr(tool, '__doc__') and tool.__doc__:
            print(f"  Doc: {tool.__doc__[:80]}...")
