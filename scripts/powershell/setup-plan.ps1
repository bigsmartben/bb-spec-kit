#!/usr/bin/env pwsh
# Setup implementation plan for a feature

[CmdletBinding()]
param(
    [switch]$Json,
    [string]$InputFile,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

# Show help if requested
if ($Help) {
    Write-Output "Usage: ./setup-plan.ps1 [-Json] -InputFile <spec.md> [-Help]"
    Write-Output "  -Json     Output results in JSON format"
    Write-Output "  -InputFile Explicit input file (must be spec.md under specs/<feature>/)"
    Write-Output "  -Help     Show this help message"
    exit 0
}

if (-not $InputFile) {
    Write-Output "ERROR: Explicit input file is required. Usage: ./setup-plan.ps1 -Json -InputFile specs/<feature>/spec.md"
    exit 1
}

# Load common functions
. "$PSScriptRoot/common.ps1"

# Resolve context from explicit input file
$paths = Get-FeaturePathsFromInputFile -InputFile $InputFile -Mode 'plan'

# Ensure the feature directory exists
New-Item -ItemType Directory -Path $paths.FEATURE_DIR -Force | Out-Null

# Copy plan template if it exists, otherwise note it or create empty file
$template = Join-Path $paths.REPO_ROOT '.specify/templates/plan-template.md'
if (Test-Path $template) { 
    Copy-Item $template $paths.IMPL_PLAN -Force
    Write-Output "Copied plan template to $($paths.IMPL_PLAN)"
} else {
    Write-Warning "Plan template not found at $template"
    # Create a basic plan file if template doesn't exist
    New-Item -ItemType File -Path $paths.IMPL_PLAN -Force | Out-Null
}

# Output results
if ($Json) {
    $result = [PSCustomObject]@{ 
        FEATURE_SPEC = $paths.FEATURE_SPEC
        IMPL_PLAN = $paths.IMPL_PLAN
        SPECS_DIR = $paths.FEATURE_DIR
        FEATURE_DIR = $paths.FEATURE_DIR
        INPUT_FILE_ABS = $paths.INPUT_FILE_ABS
        BRANCH = $paths.BRANCH
        HAS_GIT = $paths.HAS_GIT
    }
    $result | ConvertTo-Json -Compress
} else {
    Write-Output "FEATURE_SPEC: $($paths.FEATURE_SPEC)"
    Write-Output "IMPL_PLAN: $($paths.IMPL_PLAN)"
    Write-Output "SPECS_DIR: $($paths.FEATURE_DIR)"
    Write-Output "FEATURE_DIR: $($paths.FEATURE_DIR)"
    Write-Output "INPUT_FILE_ABS: $($paths.INPUT_FILE_ABS)"
    Write-Output "BRANCH: $($paths.BRANCH)"
    Write-Output "HAS_GIT: $($paths.HAS_GIT)"
}
