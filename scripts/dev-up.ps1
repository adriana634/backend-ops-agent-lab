[CmdletBinding()]
param(
    [string]$ComposeFile = 'docker-compose.yml',
    [string]$OllamaServiceName = 'ollama',
    [string]$DefaultModel = 'qwen2:0.5b',
    [switch]$Build,
    [switch]$PullModel,
    [switch]$Detached
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$InformationPreference = 'Continue'

function Write-Step {
    param(
        [Parameter(Mandatory)]
        [string]$Message
    )

    Write-Information ""
    Write-Information "==> $Message"
}

function Write-Success {
    param(
        [Parameter(Mandatory)]
        [string]$Message
    )

    Write-Information "[OK] $Message"
}

function Test-CommandAvailable {
    param(
        [Parameter(Mandatory)]
        [string]$CommandName
    )

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    return $null -ne $command
}

function Invoke-ExternalCommand {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,

        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    & $FilePath @Arguments

    if ($LASTEXITCODE -ne 0) {
        $joinedArguments = $Arguments -join ' '
        throw "Command failed: $FilePath $joinedArguments"
    }
}

function Assert-Prerequisites {
    Write-Step 'Checking prerequisites'

    if (-not (Test-CommandAvailable -CommandName 'docker')) {
        throw 'Docker is not available in PATH.'
    }

    Write-Success 'Docker is available'
}

function Start-Environment {
    param(
        [Parameter(Mandatory)]
        [string]$ComposeFilePath,

        [Parameter(Mandatory)]
        [bool]$ShouldBuild,

        [Parameter(Mandatory)]
        [bool]$RunDetached
    )

    Write-Step 'Starting development environment'

    $arguments = @('compose', '-f', $ComposeFilePath, 'up')

    if ($ShouldBuild) {
        $arguments += '--build'
    }

    if ($RunDetached) {
        $arguments += '-d'
    }

    Invoke-ExternalCommand -FilePath 'docker' -Arguments $arguments
    Write-Success 'Development environment started'
}

function Get-ContainerIdByService {
    param(
        [Parameter(Mandatory)]
        [string]$ServiceName,

        [Parameter(Mandatory=$false)]
        [string]$ComposeFilePath = $ComposeFile
    )

    try {
        $containerId = docker compose -f $ComposeFilePath ps -q $ServiceName 2>$null
        if (-not [string]::IsNullOrWhiteSpace($containerId)) {
            return ($containerId -split "`r?`n")[0]
        }
    }
    catch {
    }
    
    $containerId = docker ps --filter "name=$ServiceName" --format '{{.ID}}'

    if ([string]::IsNullOrWhiteSpace($containerId)) {
        throw "No running container found for service '$ServiceName'."
    }

    return ($containerId -split "`r?`n")[0]
}

function Install-OllamaModel {
    param(
        [Parameter(Mandatory)]
        [string]$ServiceName,

        [Parameter(Mandatory)]
        [string]$ModelName
    )

    Write-Step "Pulling Ollama model '$ModelName'"

    $containerId = Get-ContainerIdByService -ServiceName $ServiceName

    Invoke-ExternalCommand `
        -FilePath 'docker' `
        -Arguments @('exec', '-i', $containerId, 'ollama', 'pull', $ModelName)

    Write-Success "Ollama model '$ModelName' is available"
}

function Show-DetachedTips {
    param(
        [Parameter(Mandatory)]
        [string]$ComposeFilePath
    )

    Write-Step 'Detached mode tips'

    @(
        'The environment is running in the background.'
        ''
        'Recommended next step:'
        '  .\scripts\smoke-test.ps1'
        ''
        'Useful support commands:'
        "  docker compose -f $ComposeFilePath ps"
        "  docker compose -f $ComposeFilePath logs -f agent-app"
        "  docker compose -f $ComposeFilePath logs -f mock-api"
        "  docker compose -f $ComposeFilePath down"
    ) | Write-Output
}

function Show-NextSteps {
    param(
        [Parameter(Mandatory)]
        [string]$ModelName
    )

    Write-Step 'Next steps'

    @(
        'Run the smoke test:'
        '  .\scripts\smoke-test.ps1'
        ''
        'Optional manual checks:'
        '  Invoke-RestMethod http://localhost:8001/health'
        '  Invoke-RestMethod http://localhost:8000/health'
        ''
        "If needed, pull the Ollama model manually:"
        "  docker exec -it <ollama-container> ollama pull $ModelName"
    ) | Write-Output
}

function Main {
    Assert-Prerequisites

    # If user requested to pull the Ollama model, ensure the environment runs detached
    $runDetached = $Detached.IsPresent -or $PullModel.IsPresent

    Start-Environment `
        -ComposeFilePath $ComposeFile `
        -ShouldBuild:$Build.IsPresent `
        -RunDetached:$runDetached

    if ($PullModel.IsPresent) {
        Install-OllamaModel `
            -ServiceName $OllamaServiceName `
            -ModelName $DefaultModel
    }

    if ($Detached.IsPresent) {
        Show-DetachedTips -ComposeFilePath $ComposeFile
    }

    Show-NextSteps -ModelName $DefaultModel
}

try {
    Main
    exit 0
}
catch {
    Write-Error "dev-up failed: $($_.Exception.Message)"
    exit 1
}
