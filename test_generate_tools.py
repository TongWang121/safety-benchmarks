"""测试工具是否在 generate() 时被注入"""
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
from inspect_ai.dataset import Sample, MemoryDataset
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
        print(f"[DEBUG] Before generate: state.tools = {state.tools}")
        print(f"[DEBUG] Before generate: len = {len(state.tools) if state.tools else 0}")

        # 调用 generate
        state = await generate(state)

        print(f"[DEBUG] After generate: state.tools = {state.tools}")
        print(f"[DEBUG] After generate: len = {len(state.tools) if state.tools else 0}")

        return state
    return solve

@task
def test_task():
    dataset = MemoryDataset([
        Sample(id='1', input='Hello')
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
    print(f"[DEBUG] Test completed")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
