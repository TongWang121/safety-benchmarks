"""
攻击工具返回值诊断脚本

用于诊断为什么攻击工具返回 Description 而不是 attack_goal
"""

import pandas as pd
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ASB_SOURCE_DATA'))

from pyopenagi.tools.simulated_tool import AttackerTool, SimulatedTool

def test_attacker_tool():
    """测试攻击工具的返回值"""

    print("=" * 80)
    print("攻击工具返回值诊断")
    print("=" * 80)

    # 1. 加载攻击工具数据
    print("\n[1] 加载攻击工具数据...")
    attack_tools_df = pd.read_json(
        'ASB_SOURCE_DATA/data/all_attack_tools.jsonl',
        lines=True
    )

    # 查找 ResearchDataTheft
    tool_row = attack_tools_df[
        attack_tools_df['Attacker Tool'] == 'ResearchDataTheft'
    ].iloc[0]

    print(f"  攻击工具: {tool_row['Attacker Tool']}")
    print(f"  Description: {tool_row['Description']}")
    print(f"  Attack goal: {tool_row['Attack goal']}")

    # 2. 测试 AttackerTool 类
    print("\n[2] 测试 AttackerTool 类...")
    attacker_tool_dict = dict(tool_row)
    tool_instance = AttackerTool(attacker_tool_dict)

    print(f"  tool_name: {tool_instance.tool_name}")
    print(f"  tool_description: {tool_instance.tool_description}")
    print(f"  attack_goal: {tool_instance.attack_goal}")

    # 3. 调用 run() 方法
    print("\n[3] 调用 AttackerTool.run() 方法...")
    result = tool_instance.run()
    print(f"  返回值: {result}")

    # 4. 检查返回值是否包含 attack_goal
    print("\n[4] 检查返回值...")
    if tool_instance.attack_goal in result:
        print("  ✅ 返回值包含 attack_goal")
    else:
        print("  ❌ 返回值不包含 attack_goal")

    if "Ensure the security" in result:
        print("  ❌ 返回值包含 Description 文本")

    # 5. 检查是否有 SimulatedTool 的干扰
    print("\n[5] 检查正常工具...")
    normal_tools_df = pd.read_json(
        'ASB_SOURCE_DATA/data/all_normal_tools.jsonl',
        lines=True
    )

    # 查找 academic_search_agent 的工具
    agent_tools = normal_tools_df[
        normal_tools_df['Corresponding Agent'] == 'academic_search_agent'
    ]

    for _, row in agent_tools.iterrows():
        tool_name = row['Tool Name']
        print(f"\n  工具: {tool_name}")

        # 模拟 SimulatedTool 的行为
        simulated_tool = SimulatedTool(tool_name, 'ASB_SOURCE_DATA/data/all_normal_tools.jsonl')
        simulated_result = simulated_tool.run()

        if "P20230401" in simulated_result:
            print(f"    ⚠️  该工具返回值包含 'P20230401': {simulated_result[:100]}")
        else:
            print(f"    ✅ 正常工具返回值: {simulated_result[:80]}...")

    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)

    # 6. 总结
    print("\n[总结]")
    print(f"  预期攻击工具返回: You have used the attacker tool ResearchDataTheft. You have achieved the attacker goal: {tool_instance.attack_goal}")
    print(f"  实际攻击工具返回: {result}")

    if tool_instance.attack_goal in result:
        print("\n  ✅ 攻击工具返回值正确！")
        print("  如果您看到不同的输出，可能是因为：")
        print("  1. 代码版本不一致")
        print("  2. 攻击工具未被正确添加到 tool_list")
        print("  3. 某个地方使用了错误的工具实例")
    else:
        print("\n  ❌ 攻击工具返回值异常！")
        print("  请检查：")
        print("  1. add_attacker_tool() 是否被调用")
        print("  2. self.tool_list 是否包含攻击工具实例")
        print("  3. 是否有代码路径使用了错误的工具类")

if __name__ == "__main__":
    test_attacker_tool()
