"""
Quick ASB Integration Check (No imports)

Simple file and structure verification
"""

import os
from pathlib import Path

print("=" * 70)
print("ASB Quick Verification")
print("=" * 70)

# Check ASB directory
asb_dir = Path("safety-benchmarks/benchmarks/eval_benchmarks/asb")

if not asb_dir.exists():
    print(f"\n[ERROR] ASB directory not found: {asb_dir}")
    exit(1)

print(f"\n[1] ASB Directory: {asb_dir}")

# Check core files
print(f"\n[2] Core Files:")
core_files = [
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

all_exist = True
for file in core_files:
    exists = (asb_dir / file).exists()
    status = "[OK]" if exists else "[FAIL]"
    print(f"  {status} {file}")
    if not exists:
        all_exist = False

# Check data files
print(f"\n[3] Data Files:")
data_dir = asb_dir / "data"
data_files = [
    "agent_task.jsonl",
    "all_attack_tools.jsonl",
    "all_normal_tools.jsonl"
]

for file in data_files:
    path = data_dir / file
    if path.exists():
        size = path.stat().st_size
        print(f"  [OK] {file} ({size:,} bytes)")
    else:
        print(f"  [FAIL] {file} (missing)")
        all_exist = False

# Check agent configs
print(f"\n[4] Agent Configs:")
configs_dir = data_dir / "agent_configs"
if configs_dir.exists():
    configs = list(configs_dir.iterdir())
    print(f"  [OK] {len(configs)} agent configs found")
    for config in configs:
        if config.is_dir():
            print(f"      - {config.name}")
else:
    print(f"  [FAIL] Agent configs directory missing")
    all_exist = False

# Check .env file
print(f"\n[5] API Configuration:")
env_file = asb_dir / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        env_content = f.read()
        if "OPENAI_API_KEY" in env_content:
            print(f"  [OK] OPENAI_API_KEY found")
            # Show partial key
            for line in env_content.split('\n'):
                if line.startswith('OPENAI_API_KEY'):
                    key = line.split('=')[1].strip()
                    print(f"      {key[:20]}...{key[-10:]}")
        if "OPENAI_BASE_URL" in env_content:
            for line in env_content.split('\n'):
                if line.startswith('OPENAI_BASE_URL'):
                    url = line.split('=')[1].strip()
                    print(f"  [OK] OPENAI_BASE_URL: {url}")
else:
    print(f"  [FAIL] .env file not found")
    all_exist = False

# Check catalog.yaml registration
print(f"\n[6] catalog.yaml Registration:")
catalog_file = Path("safety-benchmarks/benchmarks/catalog.yaml")
if catalog_file.exists():
    with open(catalog_file, 'r', encoding='utf-8') as f:
        catalog_content = f.read()
    if "asb:" in catalog_content:
        print(f"  [OK] ASB is registered in catalog.yaml")
        # Count tasks
        import re
        tasks = re.findall(r'- name: (asb_\w+)', catalog_content)
        print(f"      Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"        - {task}")
    else:
        print(f"  [WARN] ASB not found in catalog.yaml")
else:
    print(f"  [WARN] catalog.yaml not found")

# Check _registry.py registration
print(f"\n[7] _registry.py Registration:")
registry_file = Path("safety-benchmarks/benchmarks/eval_benchmarks/_registry.py")
if registry_file.exists():
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry_content = f.read()
    if "from eval_benchmarks.asb import asb" in registry_content:
        print(f"  [OK] ASB is registered in _registry.py")
    else:
        print(f"  [WARN] ASB import not found in _registry.py")
else:
    print(f"  [WARN] _registry.py not found")

# Check score_mapper.py
print(f"\n[8] ScoreMapper Registration:")
mapper_file = Path("safety-benchmarks/score_mapper.py")
if mapper_file.exists():
    with open(mapper_file, 'r', encoding='utf-8') as f:
        mapper_content = f.read()
    asb_mappers = ["asb_asr", "asb_tsr", "asb_rr"]
    found_count = 0
    for mapper_name in asb_mappers:
        # More flexible pattern matching
        if mapper_name in mapper_content:
            print(f"  [OK] {mapper_name} Mapper found")
            found_count += 1
        else:
            print(f"  [FAIL] {mapper_name} Mapper not found")
            all_exist = False

    if found_count == len(asb_mappers):
        print(f"      All {found_count} ASB Mappers registered")
else:
    print(f"  [WARN] score_mapper.py not found")
    all_exist = False

# Summary
print(f"\n" + "=" * 70)
print(f"Verification Summary")
print(f"=" * 70)

if all_exist:
    print(f"\n[SUCCESS] All checks passed!")
    print(f"\nNext steps:")
    print(f"  1. Run: cd safety-benchmarks/benchmarks")
    print(f"  2. Setup: python ../run-eval.py --setup asb")
    print(f"  3. Test: python ../run-eval.py asb_dpi --model openai/gpt-4o-mini --limit 1")
else:
    print(f"\n[ERROR] Some checks failed")
    print(f"Please review the output above for details")
