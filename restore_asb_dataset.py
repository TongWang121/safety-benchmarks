"""
恢复 ASB 原始数据集

将数据集恢复到使用完整数据（agent_task.jsonl 和 all_attack_tools.jsonl）
"""

import shutil
from pathlib import Path
import os

print("=" * 70)
print("恢复 ASB 原始数据集")
print("=" * 70)

# 定义路径
project_root = Path(__file__).parent
data_dir = project_root / "safety-benchmarks" / "benchmarks" / "eval_benchmarks" / "asb" / "data"

print(f"\n数据目录: {data_dir}")

# 恢复备份文件
backup_files = [
    "dataset.py.bak",
]

restored_files = []

for filename in backup_files:
    backup_file = data_dir / filename
    if filename.endswith('.bak'):
        original_file = backup_file.with_suffix('')  # 移除 .bak 后缀

    if backup_file.exists():
        shutil.copy2(backup_file, original_file)
        restored_files.append(original_file.name)
        print(f"✓ 已恢复: {original_file.name}")

print(f"\n" + "=" * 70)
print(f"数据集恢复完成！")
print(f"=" * 70)
print(f"\n已恢复的文件: {', '.join(restored_files)}")
print(f"\n现在可以使用完整数据集进行测试了")
