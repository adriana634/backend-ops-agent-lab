[CmdletBinding()]
param(
    [string]$AgentBaseUrl = 'http://localhost:8000',
    [string]$MockApiBaseUrl = 'http://localhost:8001',
    [string]$IncidentId = 'INC-001'
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

function Invoke-HealthCheck {
    param(
        [Parameter(Mandatory)]
        [string]$ServiceName,

        [Parameter(Mandatory)]
        [string]$BaseUrl
    )

    Write-Step "Checking $ServiceName health"

    $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get

    if ($response.status -ne 'ok') {
        throw "$ServiceName health check returned an unexpected response."
    }

    Write-Success "$ServiceName is healthy"
    return $response
}

function Invoke-Investigation {
    param(
        [Parameter(Mandatory)]
        [string]$BaseUrl,

        [Parameter(Mandatory)]
        [string]$IncidentId
    )

    Write-Step "Calling investigate endpoint for incident '$IncidentId'"

    $body = @{
        incident_id = $IncidentId
    } | ConvertTo-Json

    $invokeCmd = Get-Command Invoke-WebRequest -ErrorAction SilentlyContinue
    $invokeParams = @{
        Uri = "$BaseUrl/investigate"
        Method = 'Post'
        ContentType = 'application/json'
        Body = $body
        ErrorAction = 'SilentlyContinue'
    }

    $invokeParams['UseBasicParsing'] = $true

    $httpResp = Invoke-WebRequest @invokeParams
    $status = $httpResp.StatusCode
    $rawBody = $httpResp.Content

    Write-Information "Investigate HTTP status: $status"
    Write-Information "Investigate raw response body:";
    Write-Output $rawBody

    try {
        $response = $rawBody | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "Investigate endpoint did not return valid JSON. Raw body: $rawBody"
    }
    
    try {
        Write-Information "";
        Write-Information "==> Recent agent-app logs (tail 200):"
        $dockerLogs = & docker compose -f docker-compose.yml logs --no-color --tail 200 agent-app 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($dockerLogs)) {
            $dockerLogs | Write-Output
        } else {
            Write-Information "No recent agent-app logs available or docker compose not accessible."
        }

        Write-Information "";
        Write-Information "==> Recent mock-api logs (tail 200):"
        $dockerLogs2 = & docker compose -f docker-compose.yml logs --no-color --tail 200 mock-api 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($dockerLogs2)) {
            $dockerLogs2 | Write-Output
        } else {
            Write-Information "No recent mock-api logs available or docker compose not accessible."
        }
    }
    catch {
        Write-Information "Could not fetch container logs: $($_.Exception.Message)"
    }

    if (-not $response.PSObject.Properties.Name -contains 'incident_id') {
        throw ('The investigate endpoint did not return incident_id. Raw JSON: ' + ($response | ConvertTo-Json -Depth 10))
    }

    if (-not $response.PSObject.Properties.Name -contains 'diagnosis') {
        throw ('The investigate endpoint did not return diagnosis. Raw JSON: ' + ($response | ConvertTo-Json -Depth 10))
    }

    Write-Success "Investigation completed"
    return $response
}

function Main {
    Write-Step 'Starting smoke test'

    [void](Invoke-HealthCheck -ServiceName 'mock-api' -BaseUrl $MockApiBaseUrl)
    [void](Invoke-HealthCheck -ServiceName 'agent-app' -BaseUrl $AgentBaseUrl)

    $investigation = Invoke-Investigation `
        -BaseUrl $AgentBaseUrl `
        -IncidentId $IncidentId

    Write-Step 'Smoke test result'
    $investigation | ConvertTo-Json -Depth 10 | Write-Output

    Write-Information ""
    Write-Success 'Smoke test completed successfully'
}

try {
    Main
    exit 0
}
catch {
    Write-Error "Smoke test failed: $($_.Exception.Message)"
    exit 1
}
