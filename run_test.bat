@echo off
REM ASB单样例测试快速启动脚本
REM 使用方法: 双击运行或在命令行执行 run_test.bat

echo ========================================
echo ASB 单样例测试 - DeepSeek v3.2
echo ========================================
echo.

REM 检查conda环境
echo [1/4] 检查conda环境...
conda activate asb
if errorlevel 1 (
    echo 错误: asb conda环境不存在
    echo 请先运行: conda create -n asb python=3.11
    pause
    exit /b 1
)

REM 检查.env文件
echo [2/4] 检查配置文件...
if not exist "ASB_SOURCE_DATA\.env" (
    echo 警告: ASB_SOURCE_DATA\.env 文件不存在
    echo 请确保API凭据已配置
    pause
)

REM 检查logs目录
echo [3/4] 准备日志目录...
if not exist "ASB_SOURCE_DATA\logs" (
    mkdir "ASB_SOURCE_DATA\logs"
)

REM 运行测试
echo [4/4] 启动测试...
echo.
echo 开始运行ASB测试，这可能需要几分钟...
echo.
cd ASB_SOURCE_DATA
python run_asb_deepseek.py
cd ..

if errorlevel 1 (
    echo.
    echo 测试失败！请检查错误信息。
    pause
    exit /b 1
)

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 结果文件: ASB_SOURCE_DATA\logs\asb_deepseek_test_results.csv
echo.
pause
