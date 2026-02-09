"""
ASB 最小化测试脚本 - 带 GBK 修复和超时

快速验证 TSR=0 修复是否有效
"""

import os
import sys
import warnings

# ========== 第一步：强制设置 UTF-8 编码（必须在任何 import 之前）==========
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')

# ========== 第二步：禁用所有警告（避免 GBK 警告刷屏）==========
warnings.filterwarnings('ignore')

# ========== 第三步：修复 importlib.metadata 的编码问题 ==========
try:
    import _locale
    _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

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
except Exception:
    pass

# ========== 第四步：设置路径和导入 ==========
from pathlib import Path
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

print("=" * 70)
print("ASB TSR=0 修复验证 - 最小化测试")
print("=" * 70)

# ========== 第五步：创建并运行 Task ==========
from eval_benchmarks.asb import asb
from inspect_ai import eval

print("\n[创建 Task]")
task = asb(
    agent_names=["financial_analyst_agent"],
    attack_type="dpi",
    limit=1,
    shuffle=False
)

print(f"数据集大小: {len(task.dataset)}")

if len(task.dataset) > 0:
    sample = task.dataset.samples[0]
    print(f"样本 ID: {sample.id}")
    print(f"任务: {sample.input[:100]}...")

# ========== 第六步：运行测试（带超时）==========
print("\n[运行评测 - 限时 2 分钟]")

import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("测试超时")

# 设置超时（仅 Unix）
if hasattr(signal, 'SIGALRM'):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(120)  # 2 分钟超时

try:
    results = eval(
        task,
        model="openai/gpt-4o-mini",
        model_args={"api_key": os.getenv("OPENAI_API_KEY")},
        log_limit=1
    )

    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)  # 取消超时

    # ========== 第七步：显示结果 ==========
    print("\n" + "=" * 70)
    print("[测试结果]")
    print("=" * 70)

    if results and len(results) > 0:
        log = results[0]

        if log.samples and len(log.samples) > 0:
            sample = log.samples[0]

            # 显示评分
            print("\n评分结果:")
            if hasattr(sample, 'scores') and sample.scores:
                for scorer_name in ["asr", "tsr", "rr"]:
                    if scorer_name in sample.scores:
                        score = sample.scores[scorer_name]
                        print(f"  {scorer_name.upper()}: {score.value:.3f}")
                        print(f"    说明: {score.explanation}")

                # 关键检查：TSR 是否 > 0
                tsr_value = sample.scores.get('tsr', None)
                if tsr_value:
                    if tsr_value.value > 0:
                        print("\n✅ 修复成功！TSR > 0")
                        print("   工具调用已恢复正常")
                    else:
                        print("\n⚠️  TSR 仍为 0，需要进一步调查")
            else:
                print("  无评分数据")

            # 显示消息统计
            if hasattr(sample, 'messages') and sample.messages:
                assistant_msgs = [m for m in sample.messages if hasattr(m, 'role') and m.role == 'assistant']
                print(f"\n消息统计:")
                print(f"  助手消息数: {len(assistant_msgs)}")

                # 检查是否包含 Action/Observation
                has_action_observation = any(
                    '[Action]:' in m.content or '[Observation]:' in m.content
                    for m in assistant_msgs
                    if hasattr(m, 'content') and m.content
                )

                if has_action_observation:
                    print("  ✅ 包含 [Action]:/[Observation]: 消息")
                else:
                    print("  ⚠️  未找到 [Action]:/[Observation]: 消息")

    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)

except TimeoutError as e:
    print(f"\n❌ 错误: {e}")
    print("测试超时（2 分钟），可能因为 LLM API 调用缓慢")

except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}")
    print(f"消息: {str(e)}")

    import traceback
    print("\n详细错误:")
    traceback.print_exc()

finally:
    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)  # 确保取消超时
