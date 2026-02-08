@echo off
REM ASB 测试脚本

echo ======================================================================
echo ASB DPI 攻击测试
echo ======================================================================

cd /d %~dp0

REM 设置虚拟环境
set VENV_PATH=.venvs\asb\Scripts\python.exe

REM 检查虚拟环境
if not exist %VENV_PATH% (
    echo [ERROR] 虚拟环境不存在，请先运行:
    echo   python -m venv .venvs/asb
    echo   .venvs\asb\Scripts\python -m pip install inspect_ai chromadb langchain pandas python-dotenv openai
    pause
    exit /b 1
)

echo [1] 虚拟环境: %VENV_PATH%

REM 运行测试
echo.
echo [2] 运行 ASB 测试...
echo.

%VENV_PATH% -c "import sys; sys.path.insert(0, 'benchmarks'); from eval_benchmarks.asb import asb; print('ASB 导入成功')"

if errorlevel 1 (
    echo [ERROR] ASB 导入失败
    pause
    exit /b 1
)

echo.
echo [SUCCESS] ASB 可以正常导入
echo.
echo 下一步: 运行完整测试（需要调用 API）
echo.
echo 如需运行完整测试，请手动执行:
echo   cd benchmarks
echo   python ../run-eval.py asb_dpi --model openai/gpt-4o-mini --limit 1
echo.

pause
