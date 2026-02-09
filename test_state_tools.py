"""测试 state.tools 的值"""
import os
import sys
import warnings
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'
warnings.filterwarnings('ignore')

# 设置 API key
from dotenv import load_dotenv
load_dotenv(Path('safety-benchmarks/benchmarks/eval_benchmarks/asb/.env'))

os.chdir(Path('safety-benchmarks'))
sys.path.insert(0, 'benchmarks')
sys.path.insert(0, '.')

from inspect_ai import Task, task
from inspect_ai.tool import tool
from inspect_ai.solver import solver, Generate
from inspect_ai.model import ChatMessageUser

@tool
def test_tool1():
    '''Test tool 1'''
    return 'result1'

@tool
def test_tool2():
    '''Test tool 2'''
    return 'result2'

@solver
def check_tools_solver():
    async def solve(state, generate: Generate):
        print(f"[DEBUG] state.tools type: {type(state.tools)}")
        print(f"[DEBUG] state.tools value: {state.tools}")
        print(f"[DEBUG] state.tools length: {len(state.tools) if state.tools else 0}")
        if state.tools:
            for t in state.tools:
                print(f"  Tool: {t.__name__}")

        # 不实际调用 LLM，直接返回
        return state
    return solve

@task
def test_task():
    from inspect_ai.dataset import Sample, MemoryDataset

    dataset = MemoryDataset([
        Sample(
            id='1',
            input='Hello'
        )
    ])

    return Task(
        dataset=dataset,
        solver=[check_tools_solver()],
        tools=[test_tool1, test_tool2]
    )

from inspect_ai import eval

try:
    results = eval(
        test_task(),
        model="openai/gpt-4o-mini"
    )
except Exception as e:
    print(f"Error: {e}")

