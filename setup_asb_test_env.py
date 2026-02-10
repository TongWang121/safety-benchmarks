"""
设置 ASB 测试环境 - 使用原始测试数据集

将 ASB_SOURCE_DATA/data/ 下的测试数据复制到 safety-benchmarks 框架的数据目录
"""

import shutil
from pathlib import Path
import os

print("=" * 70)
print("设置 ASB 测试环境")
print("=" * 70)

# 定义路径
project_root = Path(__file__).parent
source_data_dir = project_root / "ASB_SOURCE_DATA" / "data"
target_data_dir = project_root / "safety-benchmarks" / "benchmarks" / "eval_benchmarks" / "asb" / "data"

print(f"\n源数据目录: {source_data_dir}")
print(f"目标数据目录: {target_data_dir}")

# 确保目标目录存在
target_data_dir.mkdir(parents=True, exist_ok=True)

# 要复制的测试文件
test_files = [
    "agent_task_test.jsonl",
    "attack_tools_test.jsonl",
    "all_normal_tools.jsonl"  # 这个文件可能也需要
]

copied_files = []

for filename in test_files:
    source_file = source_data_dir / filename
    target_file = target_data_dir / filename

    if source_file.exists():
        # 备份原有文件（如果存在）
        if target_file.exists():
            backup_file = target_file.with_suffix(f".jsonl.bak")
            shutil.copy2(target_file, backup_file)
            print(f"✓ 已备份原有文件: {filename} -> {backup_file.name}")

        # 复制测试文件
        shutil.copy2(source_file, target_file)
        copied_files.append(filename)
        print(f"✓ 已复制测试文件: {filename}")
    else:
        print(f"✗ 源文件不存在: {source_file}")

# 修改 dataset.py 以使用测试文件
print(f"\n修改 dataset.py 以使用测试数据集...")

dataset_py = target_data_dir.parent / "dataset.py"
if dataset_py.exists():
    with open(dataset_py, 'r', encoding='utf-8') as f:
        content = f.read()

    # 备份原始文件
    with open(dataset_py.with_suffix('.py.bak'), 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ 已备份 dataset.py")

    # 修改文件名以使用测试数据集
    content = content.replace(
        'tasks_df = pd.read_json(data_dir / "agent_task.jsonl", lines=True)',
        'tasks_df = pd.read_json(data_dir / "agent_task_test.jsonl", lines=True)'
    )
    content = content.replace(
        'attack_tools_df = pd.read_json(data_dir / "all_attack_tools.jsonl", lines=True)',
        'attack_tools_df = pd.read_json(data_dir / "attack_tools_test.jsonl", lines=True)'
    )

    with open(dataset_py, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ 已修改 dataset.py 使用测试数据集")

print(f"\n" + "=" * 70)
print(f"测试环境设置完成！")
print(f"=" * 70)
print(f"\n已复制的文件: {', '.join(copied_files)}")
print(f"\n现在可以运行测试脚本了:")
print(f"  python test_asb_original_data.py")
print(f"\n恢复原始数据集:")
print(f"  python restore_asb_dataset.py")
