# Run the full pipeline locally on DuckDB (no Docker, no Airflow) – PowerShell equivalent of run_local.sh.
# Usage: .\run_local.ps1   (uses .venv\Scripts\python.exe if present)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }
$Dbt = Join-Path $PSScriptRoot ".venv\Scripts\dbt.exe"
if (-not (Test-Path $Dbt)) { $Dbt = "dbt" }

$DbPath = (Join-Path $PSScriptRoot "sephora.duckdb") -replace '\\', '/'
$env:WAREHOUSE_URL = "duckdb:///$DbPath"
$env:DUCKDB_PATH = $DbPath

# Start from a fresh database: DuckDB does not reclaim the space of dropped tables, so the file grows on every run
Remove-Item -Force -ErrorAction SilentlyContinue "$DbPath", "$DbPath.wal"

# Equivalent of `set -e` for native commands (PowerShell 5.1 does not stop on non-zero exit codes)
function Invoke-Step([string]$Dir, [string]$Exe, [string[]]$Arguments) {
    Push-Location (Join-Path $PSScriptRoot $Dir)
    # Python logging writes to stderr: with "Stop", PowerShell 5.1 would turn each line into a fatal error.
    $ErrorActionPreference = "Continue"
    try {
        & $Exe @Arguments 2>&1 | ForEach-Object { "$_" }
        if ($LASTEXITCODE -ne 0) { throw "Failed ($LASTEXITCODE): $Exe $Arguments" }
    } finally { Pop-Location }
}

Invoke-Step "src" $Python @("extract_load.py")
Invoke-Step "src" $Python @("sentiment.py")
Invoke-Step "dbt" $Dbt @("build", "--profiles-dir", ".", "--target", "duckdb")
Invoke-Step "src" $Python @("export_marts.py")
Invoke-Step "src" $Python @("dashboard_preview.py")

Write-Host "Done: marts in sephora.duckdb, CSV exports in dashboard/exports/, charts in dashboard/preview/"
