@echo off
REM =====================================================================
REM ASB 100样本测试 - 批处理脚本
REM =====================================================================
REM
REM 用途：快速运行100个样本的ASB安全测试
REM 模型：deepseek-v3.2
REM
REM 使用方法：
REM   1. 确保已配置 ASB_SOURCE_DATA\.env 文件
REM   2. 双击运行此批处理文件
REM   3. 等待测试完成，结果保存在 logs/ 目录
REM
REM =====================================================================

echo.
echo ======================================================================
echo                 ASB 100样本测试 - DeepSeek v3.2
echo ======================================================================
echo.

REM 检查conda环境
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到conda，请先安装Anaconda或Miniconda
    pause
    exit /b 1
)

REM 激活asb环境
echo [1/3] 激活conda环境...
call conda activate asb
if %errorlevel% neq 0 (
    echo [错误] 无法激活asb环境，请先创建：conda create -n asb python=3.11
    pause
    exit /b 1
)

REM 切换到ASB_SOURCE_DATA目录
echo [2/3] 切换到ASB_SOURCE_DATA目录...
cd /d "%~dp0ASB_SOURCE_DATA"
if %errorlevel% neq 0 (
    echo [错误] 无法找到ASB_SOURCE_DATA目录
    pause
    exit /b 1
)

REM 检查.env文件
if not exist .env (
    echo [错误] 未找到.env文件
    echo 请在ASB_SOURCE_DATA目录创建.env文件：
    echo   OPENAI_API_KEY=sk-xxxxx
    echo   OPENAI_BASE_URL=https://aihubmix.com/v1
    pause
    exit /b 1
)

REM 运行测试
echo [3/3] 开始运行100样本测试...
echo.
echo ======================================================================
echo.

python run_100_samples.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 测试运行失败
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo                       测试完成！
echo ======================================================================
echo.
echo 结果文件位置：ASB_SOURCE_DATA\logs\asb_100_samples_*.csv
echo.
pause
