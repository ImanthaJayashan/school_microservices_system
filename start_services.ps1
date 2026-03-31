# Run this script from the project root in PowerShell.
# It starts all microservices and gateway in separate PowerShell windows.

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
	Write-Error "Python virtual environment not found at $venvPython. Create it first with: python -m venv .venv"
	exit 1
}

$services = @(
	@{ Port = 8001; AppDir = "services/student-service/src" },
	@{ Port = 8002; AppDir = "services/teachers-service/src" },
	@{ Port = 8003; AppDir = "services/sports-service/src" },
	@{ Port = 8004; AppDir = "services/exams-service/src" },
	@{ Port = 8005; AppDir = "services/subjects-service/src" }
)

foreach ($service in $services) {
	$appDir = Join-Path $root $service.AppDir
	$command = "Set-Location '$root'; & '$venvPython' -m uvicorn app:app --port $($service.Port) --reload --app-dir '$appDir'"
	Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
}

$gatewayCommand = "Set-Location '$root'; & '$venvPython' -m uvicorn gateway.src.app:app --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $gatewayCommand

Write-Host "All services are starting..."
Write-Host "Gateway: http://127.0.0.1:8000/docs"
