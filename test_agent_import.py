"""
测试 Agent 模块导入验证
验证复制的 agent 文件能否被 Python 正确导入
"""
import os
import sys

# 添加项目路径到 Python 搜索路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=" * 60)
print("测试 Agent 模块导入")
print("=" * 60)

# 需要测试的 agents
agents = [
    "financial_analyst_agent",
    "legal_consultant_agent",
    "medical_advisor_agent",
    "education_consultant_agent",
    "psychological_counselor_agent",
    "ecommerce_manager_agent",
    "aerospace_engineer_agent",
    "academic_search_agent",
    "autonomous_driving_agent",
    "system_admin_agent",
]

for agent_name in agents:
    print(f"\n测试导入: {agent_name}")

    # 构建模块路径
    module_path = f"safety_benchmarks.benchmarks.eval_benchmarks.asb.example.{agent_name}.agent"

    try:
        # 尝试导入模块
        import importlib
        module = importlib.import_module(module_path)

        # 检查模块内容
        if hasattr(module, agent_name.replace('_', '').title().replace('_', '') + 'Agent'):
            print(f"  ✅ 模块导入成功")
            print(f"  ✅ Agent 类存在")
        else:
            # 尝试查找任何 Agent 类
            agent_classes = [name for name in dir(module) if 'Agent' in name]
            if agent_classes:
                print(f"  ✅ 模块导入成功")
                print(f"  ✅ 找到 Agent 类: {agent_classes}")
            else:
                print(f"  ⚠️  模块导入成功，但未找到 Agent 类")
                print(f"  模块内容: {dir(module)}")

    except ImportError as e:
        print(f"  ❌ 导入失败: {e}")
        print(f"  可能的原因: 缺少 __init__.py 文件或依赖问题")
    except Exception as e:
        print(f"  ❌ 其他错误: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("导入测试完成")
print("=" * 60)
