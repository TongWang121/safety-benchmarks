"""测试如何从 solver 访问 Task.attribs"""
import os
import sys
import warnings
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
load_dotenv(Path('safety-benchmarks/benchmarks/eval_benchmarks/asb/.env'))

os.chdir(Path('safety-benchmarks'))
sys.path.insert(0, 'benchmarks')
sys.path.insert(0, '.')

from inspect_ai import task, Task
from inspect_ai.tool import tool
from inspect_ai.solver import solver, Generate
from inspect_ai.dataset import Sample, MemoryDataset

@tool
def test_tool1():
    '''Test tool 1'''
    return 'result1'

@tool
def test_tool2():
    '''Test tool 2'''
    return 'result2'

@solver
def check_task_solver():
    async def solve(state, generate: Generate):
        # 尝试访问 Task
        print(f"[DEBUG] state type: {type(state)}")
        print(f"[DEBUG] state attributes: {[x for x in dir(state) if not x.startswith('_')][:20]}")

        # 检查是否有 task 属性
        if hasattr(state, 'task'):
            print(f"[DEBUG] state.task: {state.task}")
            if hasattr(state.task, 'attribs'):
                print(f"[DEBUG] state.task.attribs: {state.task.attribs}")

        return state
    return solve

@task(tools=[test_tool1, test_tool2])
def test_task_func():
    dataset = MemoryDataset([
        Sample(id='1', input='Hello')
    ])
    return Task(dataset=dataset)

from inspect_ai import eval

try:
    results = eval(
        test_task_func(),
        model="openai/gpt-4o-mini"
    )
    print(f"[DEBUG] Test completed")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
