@echo off
chcp 65001 >nul
schtasks /create /tn LongGeContentAgent /tr "D:\项目\内容自动化\run.bat" /sc DAILY /st 12:07 /f
echo Done.
pause
