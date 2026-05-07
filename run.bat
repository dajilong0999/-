@echo off
chcp 65001 >nul
echo ====================================
echo  龙哥内容自动化Agent
echo  %date% %time%
echo ====================================

cd /d D:\项目\内容自动化

:: 环境变量通过系统环境或D:\auto\run-content-agent.bat传入
python content_agent.py

echo.
echo 完成！
