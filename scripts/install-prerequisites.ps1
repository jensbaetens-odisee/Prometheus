#Requires -Version 5.1
<#
.SYNOPSIS
  Controleert en installeert ontbrekende prerequisites voor Prometheus (Windows).

.DESCRIPTION
  - Git, Python 3.12+, uv, Ollama
  - Compatibel met Windows PowerShell 5.1 (geen &&-operator)
  - Optioneel: Outlook (handmatig), winget voor installs
  - Trekt Ollama-modellen aan als ollama beschikbaar is

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\install-prerequisites.ps1

.NOTES
  Keten commando's in PowerShell 5.1 met ';' niet met '&&' (&& vereist PowerShell 7+).
#>
$ErrorActionPreference = "Continue"
$PSMajor = $PSVersionTable.PSVersion.Major

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "OK: $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "WARN: $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "FAIL: $msg" -ForegroundColor Red }

function Test-Command($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Ensure-Git {
    Write-Step "Git"
    if (Test-Command git) {
        Write-Ok (git --version)
        return $true
    }
    if (Test-Command winget) {
        Write-Warn "Git niet gevonden. Installeren via winget..."
        winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
        if (Test-Command git) { Write-Ok (git --version); return $true }
    }
    Write-Fail "Installeer Git: https://git-scm.com/download/win"
    return $false
}

function Ensure-Python {
    Write-Step "Python 3.12+"
    $py = $null
    foreach ($cmd in @("py", "python", "python3")) {
        if (Test-Command $cmd) {
            try {
                $ver = & $cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
                if ($ver -and [version]$ver -ge [version]"3.12") {
                    $py = $cmd
                    break
                }
            } catch { }
        }
    }
    if ($py) {
        Write-Ok "$py ($(& $py --version 2>&1))"
        return $true
    }
    if (Test-Command winget) {
        Write-Warn "Python 3.12+ niet gevonden. Installeren via winget..."
        winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
        if (Test-Command py) { Write-Ok (py --version); return $true }
    }
    Write-Fail "Installeer Python 3.12+: https://www.python.org/downloads/"
    return $false
}

function Refresh-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
        [System.Environment]::GetEnvironmentVariable("Path", "User")
}

function Ensure-Uv {
    Write-Step "uv (package manager)"
    if (Test-Command uv) {
        Write-Ok (uv --version)
        return $true
    }

    # winget werkt in PowerShell 5.1 (geen && in install-script)
    if (Test-Command winget) {
        Write-Warn "uv niet gevonden. Installeren via winget..."
        winget install --id astral-sh.uv -e --accept-source-agreements --accept-package-agreements
        Refresh-Path
        if (Test-Command uv) {
            Write-Ok (uv --version)
            return $true
        }
    }

    # pip fallback (geen &&)
    $pipCmd = $null
    foreach ($cmd in @("py", "python", "python3")) {
        if (Test-Command $cmd) {
            $pipCmd = $cmd
            break
        }
    }
    if ($pipCmd) {
        Write-Warn "uv installeren via pip ($pipCmd -m pip)..."
        & $pipCmd -m pip install --upgrade uv 2>&1 | Out-Host
        Refresh-Path
        if (Test-Command uv) {
            Write-Ok (uv --version)
            return $true
        }
    }

    # Officieel script alleen op PowerShell 7+ (bevat &&)
    if ($PSMajor -ge 7) {
        Write-Warn "uv installeren via astral install.ps1 (PowerShell 7+)..."
        try {
            $installScript = (Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing).Content
            Invoke-Expression $installScript
            Refresh-Path
        } catch {
            Write-Warn "uv install.ps1 mislukt: $_"
        }
        if (Test-Command uv) {
            Write-Ok (uv --version)
            return $true
        }
    }

    Write-Fail "uv niet geinstalleerd."
    Write-Warn "PowerShell 5.1: gebruik winget install astral-sh.uv OF pip install uv"
    Write-Warn "PowerShell 7+: irm https://astral.sh/uv/install.ps1 | iex"
    return $false
}

function Ensure-Ollama {
    Write-Step "Ollama"
    if (Test-Command ollama) {
        Write-Ok (ollama --version 2>&1)
        return $true
    }
    if (Test-Command winget) {
        Write-Warn "Ollama niet gevonden. Installeren via winget..."
        winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements
        Refresh-Path
    }
    if (Test-Command ollama) {
        Write-Ok (ollama --version 2>&1)
        return $true
    }
    Write-Fail "Installeer Ollama: https://ollama.com/download/windows"
    return $false
}

function Pull-OllamaModels {
    Write-Step "Ollama-modellen (optioneel, kan lang duren)"
    if (-not (Test-Command ollama)) {
        Write-Warn "Ollama niet beschikbaar; modellen overslaan."
        return
    }
    $models = @(
        "llama3.1:8b",
        "llama3.2:3b",
        "nomic-embed-text"
    )
    foreach ($m in $models) {
        Write-Host "Pull: $m ..."
        ollama pull $m 2>&1
    }
    Write-Ok "Model-pull voltooid (of gedeeltelijk)."
}

function Check-Outlook {
    Write-Step "Outlook (mail-agent, handmatig)"
    $outlookPaths = @(
        "${env:ProgramFiles}\Microsoft Office\root\Office16\OUTLOOK.EXE",
        "${env:ProgramFiles(x86)}\Microsoft Office\root\Office16\OUTLOOK.EXE"
    )
    $found = $outlookPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($found) {
        Write-Ok "Outlook gevonden: $found"
    } else {
        Write-Warn "Outlook niet gevonden. Mail-agent vereist Outlook desktop + ingelogd account."
    }
}

Write-Host "Prometheus - prerequisite installer" -ForegroundColor White
$results = @(
    (Ensure-Git),
    (Ensure-Python),
    (Ensure-Uv),
    (Ensure-Ollama)
)
Check-Outlook

$pull = Read-Host "`nOllama-modellen nu downloaden? (j/N)"
if ($pull -eq "j" -or $pull -eq "J" -or $pull -eq "y" -or $pull -eq "Y") {
    Pull-OllamaModels
}

if ($results -contains $false) {
    Write-Fail "Sommige prerequisites ontbreken. Los bovenstaande FAIL-meldingen op."
    exit 1
}

Write-Ok "Alle geautomatiseerde prerequisites zijn aanwezig."
Write-Host ""
Write-Host "Volgende stap (na Fase 0 code):" -ForegroundColor Cyan
Write-Host "  uv sync" -ForegroundColor Cyan
Write-Host "  uv run local-agents --help" -ForegroundColor Cyan
Write-Host "(In PowerShell 5.1: twee regels, of keten met ';' - niet met '&&')" -ForegroundColor DarkGray
