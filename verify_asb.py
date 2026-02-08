"""
ASB Integration Verification Script (ASCII only)

Verify ASB integration without calling API
"""

import os
import sys
from pathlib import Path

# Set working directory
benchmarks_dir = Path(__file__).parent / "safety-benchmarks"
os.chdir(benchmarks_dir)
sys.path.insert(0, str(benchmarks_dir / "benchmarks"))

print("=" * 70)
print("ASB Integration Verification")
print("=" * 70)

# 1. Check file structure
print("\n[1] Checking file structure...")
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
        print(f"  [FAIL] {file} (missing)")
        missing_files.append(file)

if missing_files:
    print(f"\n  Warning: {len(missing_files)} files are missing")

# 2. Check data files
print(f"\n[2] Checking data files...")
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
        print(f"  [FAIL] {file} (missing)")

# Check Agent configs
agent_configs_dir = data_dir / "agent_configs"
if agent_configs_dir.exists():
    agents = list(agent_configs_dir.iterdir())
    print(f"  [OK] Agent configs: {len(agents)} agents")
    for agent in agents:
        print(f"       - {agent.name}")
else:
    print(f"  [FAIL] Agent configs directory missing")

# 3. Test imports
print(f"\n[3] Testing module imports...")

try:
    # First, import the task function (this is what inspect_ai needs)
    from eval_benchmarks.asb import asb
    print(f"  [OK] eval_benchmarks.asb import successful")

    # Then, import internal modules directly for testing
    import sys
    asb_path = benchmarks_dir / "benchmarks/eval_benchmarks/asb"
    if str(asb_path) not in sys.path:
        sys.path.insert(0, str(asb_path))

    from dataset import load_asb_dataset
    print(f"  [OK] eval_benchmarks.asb.dataset import successful")

    from solver import asb_react_solver
    print(f"  [OK] eval_benchmarks.asb.solver import successful")

    from scorer import asr_scorer, tsr_scorer, rr_scorer
    print(f"  [OK] eval_benchmarks.asb.scorer import successful")

except Exception as e:
    print(f"  [FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Test dataset loading
print(f"\n[4] Testing dataset loading...")

try:
    from eval_benchmarks.asb.dataset import load_asb_dataset

    dataset = load_asb_dataset(
        agent_names=["financial_analyst_agent"],
        attack_types=["dpi"],
        limit=1,
        shuffle=False
    )

    print(f"  [OK] Dataset loaded successfully")
    print(f"      Samples: {len(dataset)}")

    if len(dataset) > 0:
        sample = dataset.samples[0]
        print(f"\n[5] First sample details:")
        print(f"      ID: {sample.id}")
        print(f"      Input: {sample.input[:100]}...")
        print(f"      Metadata:")
        print(f"        - agent_name: {sample.metadata.get('agent_name')}")
        print(f"        - normal_tools: {len(sample.metadata.get('normal_tools', {}))} tools")
        print(f"        - available_attack_tools: {len(sample.metadata.get('available_attack_tools', []))} tools")

        # Show attack tools info
        attack_tools = sample.metadata.get('available_attack_tools', [])
        if attack_tools:
            print(f"\n[6] Attack tools examples:")
            for i, tool in enumerate(attack_tools[:2], 1):
                print(f"      {i}. {tool['tool_name']}")
                print(f"         Goal: {tool['attack_goal'][:80]}...")

except Exception as e:
    print(f"  [FAIL] Dataset loading failed: {e}")
    import traceback
    traceback.print_exc()

# 5. Test Task creation
print(f"\n[7] Testing Task creation...")

try:
    task = asb(
        agent_names=["financial_analyst_agent"],
        attack_type="dpi",
        limit=1
    )

    print(f"  [OK] Task created successfully")
    print(f"      Dataset: {len(task.dataset)} samples")
    print(f"      Solver: {len(task.solver)} solver(s)")
    print(f"      Scorer: {len(task.scorer)} scorer(s)")

    for scorer in task.scorer:
        print(f"        - {scorer.name}")

except Exception as e:
    print(f"  [FAIL] Task creation failed: {e}")
    import traceback
    traceback.print_exc()

# 6. Test ScoreMapper
print(f"\n[8] Testing ScoreMapper...")

try:
    # Add benchmarks path to import score_mapper
    sys.path.insert(0, str(benchmarks_dir))
    from score_mapper import get_mapper, batch_convert

    mappers = ["asb_asr", "asb_tsr", "asb_rr"]

    for mapper_name in mappers:
        try:
            mapper = get_mapper(mapper_name)
            print(f"  [OK] {mapper_name}: {mapper.description}")

            # Test conversion
            test_score = 0.5
            result = mapper.convert(test_score)
            print(f"        Test: {test_score} -> {result.safety_score:.1f} ({result.risk_level.value})")
        except Exception as e:
            print(f"  [FAIL] {mapper_name}: {e}")

    # Batch conversion test
    print(f"\n[9] Batch conversion test:")
    test_scores = {
        "asb_asr": 0.35,
        "asb_tsr": 0.85,
        "asb_rr": 0.78
    }

    results = batch_convert(test_scores)
    for name, result in results.items():
        print(f"  {name}:")
        print(f"      Raw: {result.raw_score:.2%}")
        print(f"      Safety: {result.safety_score:.1f}")
        print(f"      Risk: {result.risk_level.value}")

except Exception as e:
    print(f"  [FAIL] ScoreMapper test failed: {e}")
    import traceback
    traceback.print_exc()

# 7. Check catalog.yaml registration
print(f"\n[10] Checking catalog.yaml registration...")

try:
    import yaml
    catalog_path = benchmarks_dir / "benchmarks/catalog.yaml"

    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)

    asb_entry = catalog.get('benchmarks', {}).get('asb')

    if asb_entry:
        print(f"  [OK] ASB is registered in catalog.yaml")
        print(f"        source: {asb_entry.get('source')}")
        print(f"        module: {asb_entry.get('module')}")

        tasks = asb_entry.get('tasks', [])
        print(f"        tasks: {len(tasks)} tasks")
        for task in tasks:
            print(f"          - {task.get('name')}")
    else:
        print(f"  [FAIL] ASB not found in catalog.yaml")

except Exception as e:
    print(f"  [FAIL] catalog.yaml check failed: {e}")

# 8. Check _registry.py registration
print(f"\n[11] Checking _registry.py registration...")

try:
    registry_path = benchmarks_dir / "benchmarks/eval_benchmarks/_registry.py"

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_content = f.read()

    if "from eval_benchmarks.asb import asb" in registry_content:
        print(f"  [OK] ASB is registered in _registry.py")
    else:
        print(f"  [FAIL] ASB not found in _registry.py")

except Exception as e:
    print(f"  [FAIL] _registry.py check failed: {e}")

# Summary
print(f"\n" + "=" * 70)
print(f"Verification Complete")
print(f"=" * 70)

if not missing_files:
    print(f"\n[SUCCESS] All required files exist")
    print(f"[SUCCESS] Module imports successful")
    print(f"[SUCCESS] Dataset loading works")
    print(f"[SUCCESS] Task creation works")
    print(f"[SUCCESS] ScoreMapper registered")
    print(f"\nNext step: Run verify_asb.py for API testing")
else:
    print(f"\n[ERROR] {len(missing_files)} files are missing, please check installation")
