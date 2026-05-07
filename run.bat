@echo off
chcp 65001 >nul
echo ====================================
echo  龙哥内容自动化Agent
echo  %date% %time%
echo ====================================

cd /d D:\项目\内容自动化

:: 设置环境变量
set DEEPSEEK_API_KEY=sk-a42cd4cc918c45c283265afb53129de7
set DEEPSEEK_BASE_URL=https://api.deepseek.com
set DEEPSEEK_MODEL=deepseek-chat
set DRAFTS_DIR=D:\项目\内容草稿箱

:: 执行
python content_agent.py >> logs.txt 2>&1

echo.
echo 完成！按任意键退出...
