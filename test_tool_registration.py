"""测试工具是否正确注册到 Task"""
import os
import sys
import warnings
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'
warnings.filterwarnings('ignore')

# 设置路径
os.chdir(Path(__file__).parent / "safety-benchmarks")
benchmarks_path = os.path.join(os.getcwd(), "benchmarks")
if benchmarks_path not in sys.path:
    sys.path.insert(0, benchmarks_path)
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from eval_benchmarks.asb import asb

# 创建 Task
task = asb(
    agent_names=["financial_analyst_agent"],
    attack_type="dpi",
    limit=1,
    shuffle=False
)

print(f"\nTask created:")
print(f"  Dataset size: {len(task.dataset)}")
print(f"  Tools: {len(task.tools) if task.tools else 0}")
print(f"  Tool names: {[t.__name__ for t in task.tools] if task.tools else []}")

# 检查第一个 sample 的 metadata
if len(task.dataset) > 0:
    sample = task.dataset.samples[0]
    normal_tools = sample.metadata.get("normal_tools", {})
    print(f"\n  Normal tools in metadata: {list(normal_tools.keys())}")

    # 测试 solver
    from inspect_ai import eval
    print(f"\n[测试 solver]")

    results = eval(
        task,
        model="openai/gpt-4o-mini",
        model_args={"api_key": os.getenv("OPENAI_API_KEY")},
        log_limit=1
    )

    if results and results[0].samples:
        sample_result = results[0].samples[0]
        if hasattr(sample_result, 'scores'):
            tsr = sample_result.scores.get('tsr', None)
            print(f"\nTSR: {tsr.value if tsr else 'N/A'}")
