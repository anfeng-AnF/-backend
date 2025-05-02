@echo off
echo ================================================================
echo 启动选课系统后端服务器
echo ================================================================

rem 激活虚拟环境
call venv\Scripts\activate

rem 检查是否激活成功
if errorlevel 1 (
    echo 激活虚拟环境失败，尝试创建新的虚拟环境...
    python -m venv venv
    call venv\Scripts\activate
)

rem 安装依赖
echo 检查并安装依赖...
pip install flask flask-cors flask-jwt-extended mysql-connector-python

rem 启动服务器
echo 启动Flask服务器...
echo 请使用 Ctrl+C 停止服务器
echo.
echo 服务器地址: http://localhost:5000
echo ================================================================
echo.

python main.py

echo.
if errorlevel 1 (
    echo 服务器出错退出，按任意键继续...
    pause > nul
) 