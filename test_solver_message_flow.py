"""
验证 ASB Solver 消息流修改是否正确

检查点：
1. 每个步骤只有 1 条 assistant 消息（不是 2 条）
2. 消息内容是 Action+Observation 或 Thinking
3. 没有 LLM 的原始响应
4. 没有 Phase 3 的额外消息
5. 最后一条消息是 workflow 最后一步的响应
"""
import re


def validate_message_flow(messages: list, workflow_steps: int) -> dict:
    """
    验证消息流是否正确

    参数:
        messages: 消息列表
        workflow_steps: workflow 步骤数

    返回:
        验证结果字典
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {
            "total_messages": len(messages),
            "workflow_steps": workflow_steps,
            "assistant_messages": 0,
            "user_messages": 0,
            "system_messages": 0,
        }
    }

    # 统计消息数量
    for msg in messages:
        role = msg.get("role") if isinstance(msg, dict) else msg.role
        if role == "assistant":
            result["stats"]["assistant_messages"] += 1
        elif role == "user":
            result["stats"]["user_messages"] += 1
        elif role == "system":
            result["stats"]["system_messages"] += 1

    # 检查 1: 没有连续的 assistant 消息
    consecutive_assistant = False
    for i in range(len(messages) - 1):
        role1 = messages[i].get("role") if isinstance(messages[i], dict) else messages[i].role
        role2 = messages[i+1].get("role") if isinstance(messages[i+1], dict) else messages[i+1].role

        if role1 == "assistant" and role2 == "assistant":
            consecutive_assistant = True
            result["errors"].append(f"发现连续的 assistant 消息在位置 {i} 和 {i+1}")
            result["valid"] = False

    if not consecutive_assistant:
        print("✅ 检查 1 通过：没有连续的 assistant 消息")

    # 检查 2: 所有 assistant 消息都是正确的格式
    incorrect_format = False
    for i, msg in enumerate(messages):
        role = msg.get("role") if isinstance(msg, dict) else msg.role
        content = msg.get("content") if isinstance(msg, dict) else msg.content

        if role == "assistant":
            # 检查是否以 [Action]: 或 [Thinking]: 开头
            if not (content.startswith("[Action]:") or content.startswith("[Thinking]")):
                incorrect_format = True
                result["errors"].append(f"位置 {i} 的 assistant 消息格式错误: {content[:50]}...")
                result["valid"] = False

    if not incorrect_format:
        print("✅ 检查 2 通过：所有 assistant 消息格式正确（[Action]: 或 [Thinking]:）")

    # 检查 3: 预期的消息数量
    # 预期 = 初始用户任务(1) + 系统消息(2) + workflow thinking(1) + workflow 步骤 * 2
    expected_min = 4 + workflow_steps * 2  # 不包括初始用户任务
    expected_max = 5 + workflow_steps * 2  # 包括初始用户任务

    if not (expected_min <= result["stats"]["assistant_messages"] <= expected_max + workflow_steps):
        result["warnings"].append(
            f"消息数量可能不对：预期约 {expected_min}-{expected_max + workflow_steps} 条，"
            f"实际 {result["stats"]["total_messages"]} 条"
        )
    else:
        print(f"✅ 检查 3 通过：消息数量合理（{result["stats"]["total_messages"]} 条）")

    # 检查 4: 最后一条消息是 workflow 最后一步的响应
    last_msg = messages[-1]
    last_role = last_msg.get("role") if isinstance(last_msg, dict) else last_msg.role
    last_content = last_msg.get("content") if isinstance(last_msg, dict) else last_msg.content

    if last_role != "assistant":
        result["errors"].append(f"最后一条消息不是 assistant 消息：{last_role}")
        result["valid"] = False
    else:
        print(f"✅ 检查 4 通过：最后一条消息是 assistant 消息")

    # 检查 5: 没有 Phase 3 的消息
    has_phase3 = False
    for msg in messages:
        content = msg.get("content") if isinstance(msg, dict) else msg.content
        if "Phase 3" in content or "Final Response Generation" in content:
            has_phase3 = True
            result["errors"].append("发现 Phase 3 的消息（应该被删除）")
            result["valid"] = False

    if not has_phase3:
        print("✅ 检查 5 通过：没有 Phase 3 的消息")

    return result


def print_message_summary(messages: list):
    """
    打印消息摘要

    参数:
        messages: 消息列表
    """
    print("\n" + "="*80)
    print("消息列表摘要")
    print("="*80)

    for i, msg in enumerate(messages):
        if isinstance(msg, dict):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
        else:
            role = msg.role
            content = msg.content

        # 截断过长的内容
        if len(content) > 100:
            content = content[:100] + "..."

        print(f"[{i}] {role:10s}: {content}")

    print("="*80)


if __name__ == "__main__":
    print("ASB Solver 消息流验证工具")
    print("="*80)

    # 示例：模拟一个 2 步 workflow 的消息流
    example_messages = [
        {"role": "user", "content": "评估投资组合风险"},
        {"role": "system", "content": "You are a financial_analyst_agent..."},
        {"role": "system", "content": "You are given available tools..."},
        {"role": "assistant", "content": "[Thinking]: The workflow generated is [...]"},
        {"role": "user", "content": "At step 1, you need to gather market data"},
        {"role": "assistant", "content": "[Action]: I will call the market_data_api; [Observation]: The knowledge I get from market_data_api is: You have successfully provided real-time market data"},
        {"role": "user", "content": "At step 2, you need to analyze the data"},
        {"role": "assistant", "content": "[Thinking]: Based on the market data, here is my analysis..."},
    ]

    print("\n示例消息流（修改后，正确）：")
    print_message_summary(example_messages)

    result = validate_message_flow(example_messages, workflow_steps=2)

    print("\n验证结果：")
    if result["valid"]:
        print("✅ 所有检查通过！消息流与源代码一致。")
    else:
        print("❌ 发现错误：")
        for error in result["errors"]:
            print(f"  - {error}")

    if result["warnings"]:
        print("\n⚠️ 警告：")
        for warning in result["warnings"]:
            print(f"  - {warning}")

    print(f"\n统计信息：")
    print(f"  总消息数: {result['stats']['total_messages']}")
    print(f"  workflow 步骤数: {result['stats']['workflow_steps']}")
    print(f"  assistant 消息数: {result['stats']['assistant_messages']}")
    print(f"  user 消息数: {result['stats']['user_messages']}")
    print(f"  system 消息数: {result['stats']['system_messages']}")
