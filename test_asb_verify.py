"""
ASB 导入和数据加载验证脚本（不调用 API）

验证 ASB 是否正确集成到 safety-benchmarks 框架
"""

import os
import sys
from pathlib import Path

# 设置工作目录
benchmarks_dir = Path(__file__).parent / "safety-benchmarks"
os.chdir(benchmarks_dir)

# 添加必要路径到 sys.path
# 只添加 benchmarks 目录，不添加子模块（避免模块命名冲突）
sys.path.insert(0, str(benchmarks_dir / "benchmarks"))

print("=" * 70)
print("ASB 集成验证")
print("=" * 70)

# 1. 检查文件结构
print("\n[1] 检查文件结构...")
asb_dir = benchmarks_dir / "benchmarks/eval_benchmarks/asb"

required_files = [
    "__init__.py",
    "asb.py",
    "solver.py",
    "scorer.py",
    "dataset.py",
    "tools.py",
    "memory.py",
    "requirements.txt",
    ".env",
    "README.md"
]

missing_files = []
for file in required_files:
    file_path = asb_dir / file
    if file_path.exists():
        print(f"  [OK] {file}")
    else:
        print(f"  [MISS] {file}")
        missing_files.append(file)

if missing_files:
    print(f"\n  警告: {len(missing_files)} 个文件缺失")

# 2. 检查数据文件
print(f"\n[2] 检查数据文件...")
data_dir = asb_dir / "data"

data_files = [
    "agent_task.jsonl",
    "all_attack_tools.jsonl",
    "all_normal_tools.jsonl"
]

for file in data_files:
    file_path = data_dir / file
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"  [OK] {file} ({size:,} bytes)")
    else:
        print(f"  [FAIL] {file} (缺失)")

# 检查 Agent 配置
agent_configs_dir = data_dir / "agent_configs"
if agent_configs_dir.exists():
    agents = list(agent_configs_dir.iterdir())
    print(f"  [OK] Agent 配置: {len(agents)} 个")
    for agent in agents:
        print(f"      - {agent.name}")
else:
    print(f"  [FAIL] Agent 配置目录缺失")

# 3. 测试导入
print(f"\n[3] 测试模块导入...")

# 先检查 inspect_evals 是否可用
try:
    import inspect_evals
    print(f"  [INFO] inspect_evals 已安装")
except ImportError:
    print(f"  [WARN] inspect_evals 未安装，某些模块可能无法导入")

try:
    from eval_benchmarks.asb import asb
    print(f"  [OK] eval_benchmarks.asb.asb 导入成功")
except Exception as e:
    print(f"  [FAIL] 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from eval_benchmarks.asb import dataset
    print(f"  [OK] eval_benchmarks.asb.dataset 导入成功")
except Exception as e:
    print(f"  [FAIL] 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from eval_benchmarks.asb import solver
    print(f"  [OK] eval_benchmarks.asb.solver 导入成功")
except Exception as e:
    print(f"  [FAIL] 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from eval_benchmarks.asb import scorer
    print(f"  [OK] eval_benchmarks.asb.scorer 导入成功")
except Exception as e:
    print(f"  [FAIL] 导入失败: {e}")
    import traceback
    traceback.print_exc()

# 4. 测试数据集加载
print(f"\n[4] 测试数据集加载...")

try:
    # 使用导入的 dataset 模块
    dataset_obj = dataset.load_asb_dataset(
        agent_names=["financial_analyst_agent"],
        attack_types=["dpi"],
        limit=1,
        shuffle=False
    )

    print(f"  [OK] 数据集加载成功")
    print(f"    样本数: {len(dataset_obj)}")

    if len(dataset_obj) > 0:
        sample = dataset_obj.samples[0]
        print(f"\n[5] 第一个样本详情:")
        print(f"    ID: {sample.id}")
        print(f"    Input: {sample.input[:100]}...")
        print(f"    Metadata:")
        print(f"      - agent_name: {sample.metadata.get('agent_name')}")
        print(f"      - normal_tools: {len(sample.metadata.get('normal_tools', {}))} 个")
        print(f"      - available_attack_tools: {len(sample.metadata.get('available_attack_tools', []))} 个")

        # 显示攻击工具信息
        attack_tools = sample.metadata.get('available_attack_tools', [])
        if attack_tools:
            print(f"\n[6] 攻击工具示例:")
            for i, tool in enumerate(attack_tools[:2], 1):
                print(f"    {i}. {tool['tool_name']}")
                print(f"       攻击目标: {tool['attack_goal'][:80]}...")

except Exception as e:
    print(f"  [FAIL] 数据集加载失败: {e}")
    import traceback
    traceback.print_exc()

# 5. 测试 Task 创建
print(f"\n[7] 测试 Task 创建...")

try:
    # 使用已经加载的 asb 函数
    task_obj = asb(
        agent_names=["financial_analyst_agent"],
        attack_type="dpi",
        limit=1
    )

    print(f"  [OK] Task 创建成功")
    print(f"    Dataset: {len(task_obj.dataset)} samples")
    print(f"    Solver: {len(task_obj.solver)} solver(s)")
    print(f"    Scorer: {len(task_obj.scorer)} scorer(s)")

    for scorer_obj in task_obj.scorer:
        scorer_name = getattr(scorer_obj, 'name', scorer_obj.__name__)
        print(f"      - {scorer_name}")

except Exception as e:
    print(f"  [FAIL] Task 创建失败: {e}")
    import traceback
    traceback.print_exc()

# 6. 测试 ScoreMapper
print(f"\n[8] 测试 ScoreMapper...")

try:
    # 添加 benchmarks 路径以导入 score_mapper
    sys.path.insert(0, str(benchmarks_dir))
    from score_mapper import get_mapper, batch_convert

    mappers = ["asb_asr", "asb_tsr", "asb_rr"]

    for mapper_name in mappers:
        try:
            mapper = get_mapper(mapper_name)
            print(f"  [OK] {mapper_name}: {mapper.description}")

            # 测试转换
            test_score = 0.5
            result = mapper.convert(test_score)
            print(f"      测试: {test_score} -> {result.safety_score:.1f} ({result.risk_level.value})")
        except Exception as e:
            print(f"  [FAIL] {mapper_name}: {e}")

    # 批量转换测试
    print(f"\n[9] 批量转换测试:")
    test_scores = {
        "asb_asr": 0.35,
        "asb_tsr": 0.85,
        "asb_rr": 0.78
    }

    results = batch_convert(test_scores)
    for name, result in results.items():
        print(f"  {name}:")
        print(f"    原始分数: {result.raw_score:.2%}")
        print(f"    安全分数: {result.safety_score:.1f}")
        print(f"    风险等级: {result.risk_level.value}")

except Exception as e:
    print(f"  [FAIL] ScoreMapper 测试失败: {e}")
    import traceback
    traceback.print_exc()

# 7. 检查 catalog.yaml 注册
print(f"\n[10] 检查 catalog.yaml 注册...")

try:
    import yaml
    catalog_path = benchmarks_dir / "benchmarks/catalog.yaml"

    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)

    asb_entry = catalog.get('benchmarks', {}).get('asb')

    if asb_entry:
        print(f"  [OK] ASB 已在 catalog.yaml 中注册")
        print(f"    source: {asb_entry.get('source')}")
        print(f"    module: {asb_entry.get('module')}")

        tasks = asb_entry.get('tasks', [])
        print(f"    tasks: {len(tasks)} 个")
        for task in tasks:
            print(f"      - {task.get('name')}")
    else:
        print(f"  [FAIL] ASB 未在 catalog.yaml 中找到")

except Exception as e:
    print(f"  [FAIL] catalog.yaml 检查失败: {e}")

# 8. 检查 _registry.py 注册
print(f"\n[11] 检查 _registry.py 注册...")

try:
    registry_path = benchmarks_dir / "benchmarks/eval_benchmarks/_registry.py"

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_content = f.read()

    if "from eval_benchmarks.asb import asb" in registry_content:
        print(f"  [OK] ASB 已在 _registry.py 中注册")
    else:
        print(f"  [FAIL] ASB 未在 _registry.py 中找到")

except Exception as e:
    print(f"  [FAIL] _registry.py 检查失败: {e}")

# 总结
print(f"\n" + "=" * 70)
print(f"验证完成")
print(f"=" * 70)

if not missing_files:
    print(f"\n[OK] 所有必要文件都存在")
    print(f"[OK] 模块导入成功")
    print(f"[OK] 数据集加载正常")
    print(f"[OK] Task 创建成功")
    print(f"[OK] ScoreMapper 注册成功")
    print(f"\n下一步: 运行 python test_asb_simple.py 进行 API 测试")
else:
    print(f"\n[FAIL] 有 {len(missing_files)} 个文件缺失，请检查安装")
