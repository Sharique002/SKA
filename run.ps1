param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $ProjectRoot "frontend"
$RuntimeDir = Join-Path ([System.IO.Path]::GetTempPath()) "SKA_01_runtime"
$BackendUrl = "http://127.0.0.1:5000/api/health"
$FrontendUrl = "http://127.0.0.1:3000/"
$StartedProcesses = @()

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host $Message -ForegroundColor Cyan
}

function Test-Url {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
    } catch {
        return $false
    }
}

function Wait-ForUrl {
    param(
        [string]$Name,
        [string]$Url,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Url $Url) {
            Write-Host "[OK] $Name is ready" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Seconds 1
    }

    return $false
}

function Show-LogTail {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Write-Host ""
        Write-Host "Last log lines from $Path" -ForegroundColor Yellow
        Get-Content -LiteralPath $Path -Tail 40
    }
}

function Test-NativeCommand {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    try {
        & $FilePath @Arguments *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Get-ToolPath {
    param(
        [string[]]$Names,
        [string]$FriendlyName,
        [string[]]$VersionArguments = @("--version")
    )

    foreach ($name in $Names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command -and (Test-NativeCommand -FilePath $command.Source -Arguments $VersionArguments)) {
            return $command.Source
        }
    }

    throw "$FriendlyName was not found. Install it, then run this script again."
}

function Ensure-Python {
    $venvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"

    if (Test-Path -LiteralPath $venvPython) {
        if (Test-NativeCommand -FilePath $venvPython -Arguments @("--version")) {
            return $venvPython
        }
    }

    $systemPython = Get-ToolPath -Names @("python.exe", "python") -FriendlyName "Python"

    Write-Step "Creating Python virtual environment"
    & $systemPython -m venv (Join-Path $ProjectRoot "venv")

    if (!(Test-Path -LiteralPath $venvPython)) {
        throw "Could not create venv\Scripts\python.exe"
    }

    return $venvPython
}

function Ensure-BackendDependencies {
    param([string]$PythonExe)

    if (Test-NativeCommand -FilePath $PythonExe -Arguments @("-c", "import flask, flask_cors")) {
        return
    }

    Write-Step "Installing backend dependencies"
    & $PythonExe -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
}

function Ensure-FrontendDependencies {
    $viteScript = Join-Path $FrontendDir "node_modules\vite\bin\vite.js"
    if (Test-Path -LiteralPath $viteScript) {
        return
    }

    $npm = Get-ToolPath -Names @("npm.cmd", "npm") -FriendlyName "npm"

    Write-Step "Installing frontend dependencies"
    Push-Location $FrontendDir
    try {
        & $npm install
    } finally {
        Pop-Location
    }
}

function Start-Backend {
    param([string]$PythonExe)

    if (Test-Url $BackendUrl) {
        Write-Host "[OK] Backend already running at $BackendUrl" -ForegroundColor Green
        return $null
    }

    Write-Step "Starting backend on port 5000"
    $backendLog = Join-Path $RuntimeDir "backend.log"
    $backendErr = Join-Path $RuntimeDir "backend.err"
    $args = @(
        "-m", "flask",
        "--app", "backend.app",
        "run",
        "--host", "0.0.0.0",
        "--port", "5000",
        "--no-debugger",
        "--no-reload"
    )

    $process = Start-Process `
        -FilePath $PythonExe `
        -ArgumentList $args `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $backendLog `
        -RedirectStandardError $backendErr `
        -PassThru

    if (!(Wait-ForUrl -Name "Backend" -Url $BackendUrl)) {
        Show-LogTail $backendLog
        Show-LogTail $backendErr
        throw "Backend did not start. Check the logs above."
    }

    return $process
}

function Start-Frontend {
    if (Test-Url $FrontendUrl) {
        Write-Host "[OK] Frontend already running at $FrontendUrl" -ForegroundColor Green
        return $null
    }

    $node = Get-ToolPath -Names @("node.exe", "node") -FriendlyName "Node.js"

    Write-Step "Starting frontend on port 3000"
    $frontendLog = Join-Path $RuntimeDir "frontend.log"
    $frontendErr = Join-Path $RuntimeDir "frontend.err"
    $args = @("node_modules\vite\bin\vite.js", "--host", "127.0.0.1")

    $process = Start-Process `
        -FilePath $node `
        -ArgumentList $args `
        -WorkingDirectory $FrontendDir `
        -RedirectStandardOutput $frontendLog `
        -RedirectStandardError $frontendErr `
        -PassThru

    if (!(Wait-ForUrl -Name "Frontend" -Url $FrontendUrl)) {
        Show-LogTail $frontendLog
        Show-LogTail $frontendErr
        throw "Frontend did not start. Check the logs above."
    }

    return $process
}

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
Set-Location $ProjectRoot

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Smart Knowledge Assistant" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$python = Ensure-Python
Ensure-BackendDependencies -PythonExe $python
Ensure-FrontendDependencies

if ($CheckOnly) {
    Write-Host ""
    Write-Host "[OK] Project dependencies look ready." -ForegroundColor Green
    exit 0
}

try {
    $backendProcess = Start-Backend -PythonExe $python
    if ($backendProcess) {
        $StartedProcesses += $backendProcess
    }

    $frontendProcess = Start-Frontend
    if ($frontendProcess) {
        $StartedProcesses += $frontendProcess
    }

    Write-Host ""
    Write-Host "Application is running:" -ForegroundColor Green
    Write-Host "  Frontend: http://127.0.0.1:3000/"
    Write-Host "  Backend:  http://127.0.0.1:5000/api/health"
    Write-Host ""
    Write-Host "Logs are stored in: $RuntimeDir"
    Write-Host "Press Ctrl+C to stop services started by this script."

    while ($true) {
        foreach ($process in $StartedProcesses) {
            if ($process.HasExited) {
                throw "$($process.ProcessName) exited unexpectedly."
            }
        }
        Start-Sleep -Seconds 2
    }
} finally {
    foreach ($process in $StartedProcesses) {
        if ($process -and !$process.HasExited) {
            Stop-Process -Id $process.Id -ErrorAction SilentlyContinue
        }
    }
}
