# Run this script from the project root in PowerShell.
# It starts all microservices and gateway in separate PowerShell windows.

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root/services/student-service/src'; uvicorn app:app --port 8001 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root/services/teachers-service/src'; uvicorn app:app --port 8002 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root/services/sports-service/src'; uvicorn app:app --port 8003 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root/services/exams-service/src'; uvicorn app:app --port 8004 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root/services/subjects-service/src'; uvicorn app:app --port 8005 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; uvicorn gateway.src.app:app --port 8080 --reload"

Write-Host "All services are starting..."
Write-Host "Gateway: http://127.0.0.1:8080/docs"
