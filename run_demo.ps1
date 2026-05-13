$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Installing dependencies..."
& .\.venv\Scripts\python -m pip install -r requirements.txt

Write-Host "Synchronizing processed data..."
& .\.venv\Scripts\python src\sync_processed_data.py

Write-Host "Running analysis..."
& .\.venv\Scripts\python src\run_analysis.py

Write-Host ""
Write-Host "Demo run completed successfully."
Write-Host "Generated tables are available in output\tables."
