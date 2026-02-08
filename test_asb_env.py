"""
ASB 环境测试脚本（使用虚拟环境）

直接在虚拟环境中运行测试
"""

import subprocess
import sys
from pathlib import Path

print("=" * 70)
print("ASB 环境测试")
print("=" * 70)

# 虚拟环境路径
venv_dir = Path("safety-benchmarks/.venvs/asb")
if sys.platform == "win32":
    python_exe = venv_dir / "Scripts/python.exe"
else:
    python_exe = venv_dir / "bin/python"

if not python_exe.exists():
    print(f"\n[ERROR] 虚拟环境不存在: {venv_dir}")
    sys.exit(1)

print(f"\n虚拟环境 Python: {python_exe}")

# 测试 inspect_ai 导入
print(f"\n[1] 测试 inspect_ai 导入...")

result = subprocess.run(
    [str(python_exe), "-c", "import inspect_ai; print('Version:', inspect_ai.__version__)"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print(f"  [OK] {result.stdout.strip()}")
else:
    print(f"  [FAIL] {result.stderr}")
    sys.exit(1)

# 测试 ASB 数据集加载
print(f"\n[2] 测试 ASB 数据集加载...")

test_code = """
import sys
sys.path.insert(0, 'benchmarks')

from eval_benchmarks.asb.dataset import load_asb_dataset

dataset = load_asb_dataset(
    agent_names=['financial_analyst_agent'],
    attack_types=['dpi'],
    limit=1,
    shuffle=False
)

print(f'  数据集大小: {len(dataset)}')

if len(dataset) > 0:
    sample = dataset.samples[0]
    print(f'  样本 ID: {sample.id}')
    print(f'  Input: {sample.input[:100]}...')
    print(f'  Agent: {sample.metadata.get(\"agent_name\")}')
    print(f'  正常工具: {len(sample.metadata.get(\"normal_tools\", {}))} 个')
    print(f'  攻击工具: {len(sample.metadata.get(\"available_attack_tools\", []))} 个')
"""

result = subprocess.run(
    [str(python_exe), "-c", test_code],
    capture_output=True,
    text=True,
    cwd=Path(__file__).parent
)

if result.returncode == 0:
    print(result.stdout)
else:
    print(f"  [FAIL] 数据集加载失败")
    print(f"  错误: {result.stderr}")
    # 但这可能是预期的，因为其他 benchmark 有问题

# 创建简化的测试脚本
print(f"\n[3] 创建简化测试脚本...")

test_script = """
import os
import sys
from pathlib import Path

# 添加路径
asb_dir = Path('safety-benchmarks/benchmarks/eval_benchmarks/asb')
sys.path.insert(0, str(asb_dir))

# 加载环境
from dotenv import load_dotenv
load_dotenv(asb_dir / '.env')

# 导入模块
from dataset import load_asb_dataset
from solver import asb_react_solver
from scorer import asr_scorer, tsr_scorer, rr_scorer
from inspect_ai import task, Task, GenerateConfig, eval

# 创建数据集
dataset = load_asb_dataset(
    agent_names=['financial_analyst_agent'],
    attack_types=['dpi'],
    limit=1,
    shuffle=False
)

print(f'数据集大小: {len(dataset)}')

if len(dataset) > 0:
    sample = dataset.samples[0]
    print(f'样本 ID: {sample.id}')
    print(f'Input: {sample.input[:100]}...')

    # 选择攻击工具
    import random
    attack_tools = sample.metadata.get('available_attack_tools', [])
    if attack_tools:
        tool = random.choice(attack_tools)
        sample.metadata['attacker_goal'] = tool['attack_goal']
        print(f'攻击工具: {tool[\"tool_name\"]}')
        print(f'攻击目标: {tool[\"attack_goal\"][:80]}...')

# 定义 Task
@task
def test_asb_task():
    return Task(
        dataset=dataset,
        solver=[asb_react_solver(attack_type='dpi', temperature=0.0)],
        scorer=[asr_scorer(), tsr_scorer(), rr_scorer()],
        config=GenerateConfig(temperature=0.0, max_tokens=256)
    )

# 运行评测
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL')

print(f'\\n开始评测...')
print(f'API: {base_url}')

results = eval(
    test_asb_task(),
    model='openai/gpt-4o-mini',
    model_args={
        'api_key': api_key,
        'base_url': base_url,
    },
    log_limit=3
)

if results and len(results) > 0:
    result = results[0]
    print(f'\\n状态: {result.status}')

    if hasattr(result, 'scores'):
        for name, score in result.scores.items():
            print(f'  {name.upper()}: {score.value:.4f}')
            print(f'    {score.explanation}')

    if hasattr(result, 'messages'):
        assistant_msgs = [m for m in result.messages if hasattr(m, 'role') and m.role == 'assistant']
        if assistant_msgs:
            last_msg = assistant_msgs[-1]
            content = last_msg.content if hasattr(last_msg, 'content') else ''
            print(f'\\n响应长度: {len(content)} 字符')
            print(f'响应预览: {content[:200]}...')

print('\\n测试完成!')
"""

# 写入测试脚本
test_script_path = Path("safety_benchmarks/test_asb_bg.py")
test_script_path.write_text(test_script)

print(f"  [OK] 测试脚本已创建: {test_script_path}")

# 运行测试
print(f"\n[4] 运行测试...")
print(f"  这可能需要 10-30 秒...")

result = subprocess.run(
    [str(python_exe), str(test_script_path.name)],
    capture_output=False,  # 实时显示输出
    text=True,
    cwd=Path("safety-benchmarks")
)

if result.returncode == 0:
    print(f"\n[SUCCESS] 测试完成")
else:
    print(f"\n[ERROR] 测试失败")

# 清理
# test_script_path.unlink()  # 保留脚本以便调试

print(f"\n" + "=" * 70)
print(f"环境测试完成")
print(f"=" * 70)
