"""
ASB DPI 攻击测试 - 使用原始测试数据集

使用 ASB_SOURCE_DATA/data/ 目录下的测试数据，验证消息流一致性

注意：运行此脚本前，请先运行 setup_asb_test_env.py 来设置测试环境
"""

import os
import sys
from pathlib import Path

# 修复 Windows 编码问题
os.environ['PYTHONIOENCODING'] = 'utf-8'
import _locale
_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

if sys.platform == 'win32':
    try:
        import importlib.metadata as _metadata
        if hasattr(_metadata, 'Distribution'):
            _original_read = _metadata.Distribution.read

            def _patched_read(self, filename, *args, **kwargs):
                result = _original_read(self, filename, *args, **kwargs)
                if isinstance(result, bytes):
                    try:
                        return result.decode('utf-8')
                    except UnicodeDecodeError:
                        return result.decode('gbk', errors='ignore')
                return result

            _metadata.Distribution.read = _patched_read
    except Exception as e:
        print(f"编码修复失败: {e}")

# 设置工作目录
os.chdir(Path(__file__).parent)
benchmarks_path = os.path.join(os.getcwd(), "safety-benchmarks", "benchmarks")
if benchmarks_path not in sys.path:
    sys.path.insert(0, benchmarks_path)

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

# 加载环境变量
from dotenv import load_dotenv
env_path = Path("safety-benchmarks/benchmarks/eval_benchmarks/asb/.env")
load_dotenv(env_path)

print("=" * 70)
print("ASB DPI 攻击测试 - 使用原始测试数据集")
print("=" * 70)

# 检查测试环境是否已设置
data_dir = Path("safety-benchmarks/benchmarks/eval_benchmarks/asb/data")
test_task_file = data_dir / "agent_task_test.jsonl"

if not test_task_file.exists():
    print(f"\n⚠️  测试环境未设置！")
    print(f"\n请先运行: python setup_asb_test_env.py")
    print(f"这将复制 ASB_SOURCE_DATA/data/ 下的测试数据到框架数据目录")
    sys.exit(1)

# 导入并创建 Task
from eval_benchmarks.asb import asb

# 创建单个样本的测试任务
task = asb(
    agent_names=["financial_analyst_agent"],
    attack_type="dpi",
    limit=1,  # 只测试 1 个样本
    shuffle=False
)

print(f"\n数据集大小: {len(task.dataset)}")

if len(task.dataset) > 0:
    sample = task.dataset.samples[0]
    print(f"样本 ID: {sample.id}")
    print(f"任务输入: {sample.input[:100]}...")

    # 运行测试
    print(f"\n[运行评测]")
    from inspect_ai import eval

    results = eval(
        task,
        model="openai/gpt-4o-mini",
        model_args={"api_key": os.getenv("OPENAI_API_KEY")},
        log_limit=10
    )

    # 显示结果
    if results and len(results) > 0:
        log = results[0]
        if log.samples and len(log.samples) > 0:
            sample_result = log.samples[0]

            print(f"\n[消息流分析]")
            print("=" * 70)

            if hasattr(sample_result, 'messages') and sample_result.messages:
                for i, msg in enumerate(sample_result.messages):
                    role = getattr(msg, 'role', 'unknown')
                    content = getattr(msg, 'content', '')

                    # 只显示 user 和 assistant 消息
                    if role in ['user', 'assistant']:
                        content_preview = content[:100] if len(content) > 100 else content
                        print(f"\n{i}. {role.upper()}")
                        print(f"   {content_preview}...")

                        # 检查是否有 [Thinking]: 前缀
                        if '[Thinking]:' in content:
                            print(f"   ✓ 包含 [Thinking]: 前缀")

            print(f"\n[评分结果]")
            print("=" * 70)
            if hasattr(sample_result, 'scores') and sample_result.scores:
                for scorer_name in ["asr", "tsr", "rr"]:
                    if scorer_name in sample_result.scores:
                        score = sample_result.scores[scorer_name]
                        print(f"{scorer_name.upper()}: {score.value:.3f} - {score.explanation}")

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)
