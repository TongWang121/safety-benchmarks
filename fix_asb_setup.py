"""
ASB 环境设置修复脚本

解决 inspect_ai 缺失的问题
"""

import subprocess
import sys
from pathlib import Path

print("=" * 70)
print("ASB 环境设置修复")
print("=" * 70)

# 检查虚拟环境是否存在
venv_path = Path("safety-benchmarks/.venvs/asb")

if venv_path.exists():
    print(f"\n[1] 虚拟环境已存在: {venv_path}")

    # 获取 Python 路径
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    if python_exe.exists():
        print(f"  Python: {python_exe}")
    else:
        print(f"  [ERROR] Python not found: {python_exe}")
        sys.exit(1)

else:
    print(f"\n[ERROR] 虚拟环境不存在: {venv_path}")
    print(f"\n请先运行:")
    print(f"  cd safety-benchmarks/benchmarks")
    print(f"  python ../run-eval.py --setup asb")
    sys.exit(1)

# 安装 inspect_ai
print(f"\n[2] 安装 inspect_ai...")

try:
    result = subprocess.run(
        [str(python_exe), "-m", "pip", "install", "inspect_ai"],
        capture_output=True,
        text=True,
        timeout=300  # 5 分钟超时
    )

    if result.returncode == 0:
        print(f"  [SUCCESS] inspect_ai 安装成功")
        print(f"\n安装输出:")
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    else:
        print(f"  [ERROR] inspect_ai 安装失败")
        print(f"\n错误信息:")
        print(result.stderr)
        sys.exit(1)

except subprocess.TimeoutExpired:
    print(f"  [ERROR] 安装超时（5分钟）")
    sys.exit(1)
except Exception as e:
    print(f"  [ERROR] 安装失败: {e}")
    sys.exit(1)

# 安装其他依赖
print(f"\n[3] 安装其他依赖...")

requirements = [
    "chromadb>=0.4.0",
    "langchain>=0.1.0",
    "pandas>=2.0.0",
    "openai>=1.0.0",
    "python-dotenv"
]

for req in requirements:
    print(f"  安装 {req}...")
    result = subprocess.run(
        [str(python_exe), "-m", "pip", "install", req],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode == 0:
        print(f"    [OK] {req}")
    else:
        print(f"    [WARN] {req} 安装失败（可能已安装）")

# 验证安装
print(f"\n[4] 验证安装...")

result = subprocess.run(
    [str(python_exe), "-c", "import inspect_ai; print('inspect_ai version:', inspect_ai.__version__)"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print(f"  [SUCCESS] {result.stdout.strip()}")
else:
    print(f"  [WARN] inspect_ai 导入测试失败")
    print(f"  {result.stderr}")

# 测试 ASB 导入
print(f"\n[5] 测试 ASB 导入...")

result = subprocess.run(
    [str(python_exe), "-c", "from eval_benchmarks.asb import asb; print('ASB import: OK')"],
    capture_output=True,
    text=True,
    cwd=Path("safety-benchmarks/benchmarks")
)

if result.returncode == 0:
    print(f"  [SUCCESS] {result.stdout.strip()}")
else:
    print(f"  [WARN] ASB 导入测试失败")
    print(f"  {result.stderr}")

# 总结
print(f"\n" + "=" * 70)
print(f"修复完成")
print(f"=" * 70)

print(f"\n下一步:")
print(f"  cd safety-benchmarks/benchmarks")
print(f"  python ../run-eval.py asb_dpi --model openai/gpt-4o-mini --limit 1")
