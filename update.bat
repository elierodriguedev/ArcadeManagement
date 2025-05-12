
@echo off
echo [UpdateScript] Starting update process... >> update_log.txt
echo [UpdateScript] Current directory: %CD% >> update_log.txt
echo [UpdateScript] Attempting to delete old agent.log... >> update_log.txt
del "agent.log" > NUL 2>&1
echo [UpdateScript] Attempting to terminate old agent.exe process... >> update_log.txt
taskkill /F /IM agent.exe
timeout /T 5 /nobreak > NUL
echo [UpdateScript] Attempting to delete old agent.exe... >> update_log.txt
del "agent.exe"
echo [UpdateScript] Attempting to rename agent_new.exe to agent.exe... >> update_log.txt
rename "agent_new.exe" "agent.exe"
echo [UpdateScript] Attempting to start new agent.exe... >> update_log.txt
start "" "agent.exe"
echo [UpdateScript] Update script finished. >> update_log.txt
