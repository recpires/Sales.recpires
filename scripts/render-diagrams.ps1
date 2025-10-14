param()

Write-Host "Rendering PlantUML diagrams (PowerShell)"

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

$workspace = Resolve-Path ".."
$outDir = Join-Path $workspace "docs\diagrams\generated"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

Write-Host "Using Docker image plantuml/plantuml to render files..."

#$dockerCmd = "docker run --rm -v `"$($workspace):/workspace`" plantuml/plantuml:latest -tpng docs/diagrams/*.puml -o docs/diagrams/generated"
try {
    docker --version > $null 2>&1
} catch {
    Write-Error "Docker is not available. Please install Docker and retry."
    exit 1
}

$cmd = "docker run --rm -v `"$($workspace):/workspace`" plantuml/plantuml:latest -tpng docs/diagrams/*.puml -o docs/diagrams/generated"
Write-Host "Running: $cmd"
Invoke-Expression $cmd

Write-Host "Rendered diagrams saved to: $outDir"
Write-Host "You can commit the generated files if you want them tracked in the repo."
