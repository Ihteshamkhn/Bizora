$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Starting Bizora..."

$backend = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$root\\backend'; ..\\venv\\Scripts\\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000" -PassThru
$frontend = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$root\\frontend'; npm run dev" -PassThru

Write-Host "Backend started: http://localhost:8000/docs"
Write-Host "Frontend started: http://localhost:3000"
Write-Host "To stop later, close the PowerShell windows or use Ctrl+C in each terminal."
