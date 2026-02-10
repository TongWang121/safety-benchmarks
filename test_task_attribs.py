"""测试 @task 装饰器的 tools 参数"""
import os
import sys
import warnings
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'
warnings.filterwarnings('ignore')

os.chdir(Path('safety-benchmarks'))
sys.path.insert(0, 'benchmarks')
sys.path.insert(0, '.')

from inspect_ai import task, Task
from inspect_ai.tool import tool
from inspect_ai.dataset import Sample, MemoryDataset

@tool
def test_tool1():
    '''Test tool 1'''
    return 'result1'

@tool
def test_tool2():
    '''Test tool 2'''
    return 'result2'

# 创建 Task，传递 tools 参数
@task(tools=[test_tool1, test_tool2])
def test_task_func():
    dataset = MemoryDataset([
        Sample(id='1', input='Hello')
    ])
    return Task(dataset=dataset)

# 获取 Task 实例
t = test_task_func()

# 检查 Task 的属性
print(f"Task type: {type(t)}")
print(f"Task attribs: {t.attribs}")
print(f"Task attribs keys: {t.attribs.keys() if t.attribs else []}")

# 检查 attribs 中是否有 tools
if t.attribs and 'tools' in t.attribs:
    print(f"Tools in attribs: {t.attribs['tools']}")
