"""
测试 agent_path 解析验证脚本
验证 metadata 中的 agent_path 能否正确解析到 example 目录中的文件
"""
import os
import json

# 基础路径
BASE_DIR = "safety-benchmarks/benchmarks/eval_benchmarks/asb"
EXAMPLE_DIR = os.path.join(BASE_DIR, "example")
AGENT_TASK_FILE = os.path.join(BASE_DIR, "data", "agent_task.jsonl")

print("=" * 60)
print("验证 agent_path 解析")
print("=" * 60)

# 读取 agent_task.jsonl
with open(AGENT_TASK_FILE, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        if not line.strip():
            continue

        agent_info = json.loads(line)
        agent_name = agent_info["agent_name"]
        agent_path = agent_info["agent_path"]

        print(f"\n[Agent {line_num}] {agent_name}")
        print(f"  agent_path: {agent_path}")

        # 构建完整路径
        full_path = os.path.join(BASE_DIR, agent_path)
        print(f"  完整路径: {full_path}")

        # 检查目录是否存在
        if os.path.exists(full_path):
            print(f"  ✅ 目录存在")

            # 检查必需文件
            required_files = ["agent.py", "config.json", "meta_requirements.txt"]
            for file_name in required_files:
                file_path = os.path.join(full_path, file_name)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"    ✅ {file_name} ({file_size} bytes)")
                else:
                    print(f"    ❌ {file_name} 缺失")

            # 尝试读取 agent.py 验证语法
            agent_py_path = os.path.join(full_path, "agent.py")
            try:
                with open(agent_py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单检查是否包含类定义
                    if "class" in content and "Agent" in content:
                        print(f"    ✅ agent.py 包含 Agent 类定义")
                    else:
                        print(f"    ⚠️  agent.py 可能缺少 Agent 类")
            except Exception as e:
                print(f"    ❌ 读取 agent.py 失败: {e}")

        else:
            print(f"  ❌ 目录不存在")

        # 尝试通过 Python 导入
        try:
            # 将路径转换为 Python 模块路径
            # example/system_admin_agent -> eval_benchmarks.asb.example.system_admin_agent
            module_path = f"eval_benchmarks.asb.{agent_path.replace('/', '.')}"
            print(f"  模块路径: {module_path}")

            # 注意：这里只验证路径格式，不实际导入（因为可能有依赖问题）
            if agent_path.startswith("example/"):
                print(f"  ✅ 路径格式正确（以 example/ 开头）")
            else:
                print(f"  ⚠️  路径格式可能不正确")

        except Exception as e:
            print(f"  ❌ 路径验证失败: {e}")

print("\n" + "=" * 60)
print("验证完成")
print("=" * 60)
