#!/usr/bin/env pwsh
# Common PowerShell functions analogous to common.sh

function Get-RepoRoot {
    try {
        $result = git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $result
        }
    } catch {
        # Git command failed
    }
    
    # Fall back to script location for non-git repos
    return (Resolve-Path (Join-Path $PSScriptRoot "../../..")).Path
}

function Get-CurrentBranch {
    # First check if SPECIFY_FEATURE environment variable is set
    if ($env:SPECIFY_FEATURE) {
        return $env:SPECIFY_FEATURE
    }
    
    # Then check git if available
    try {
        $result = git rev-parse --abbrev-ref HEAD 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $result
        }
    } catch {
        # Git command failed
    }
    
    # For non-git repos, try to find the latest feature directory
    $repoRoot = Get-RepoRoot
    $specsDir = Join-Path $repoRoot "specs"
    
    if (Test-Path $specsDir) {
        $latestFeature = ""
        $highest = 0
        
        Get-ChildItem -Path $specsDir -Directory | ForEach-Object {
            if ($_.Name -match '^(\d{3})-') {
                $num = [int]$matches[1]
                if ($num -gt $highest) {
                    $highest = $num
                    $latestFeature = $_.Name
                }
            }
        }
        
        if ($latestFeature) {
            return $latestFeature
        }
    }
    
    # Final fallback
    return "main"
}

function Test-HasGit {
    try {
        git rev-parse --show-toplevel 2>$null | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Test-FeatureBranch {
    param(
        [string]$Branch,
        [bool]$HasGit = $true
    )
    
    # For non-git repos, we can't enforce branch naming but still provide output
    if (-not $HasGit) {
        Write-Warning "[specify] Warning: Git repository not detected; skipped branch validation"
        return $true
    }
    
    if ($Branch -notmatch '^[0-9]{3}-') {
        Write-Output "ERROR: Not on a feature branch. Current branch: $Branch"
        Write-Output "Feature branches should be named like: 001-feature-name"
        return $false
    }
    return $true
}

function Get-FeatureDir {
    param([string]$RepoRoot, [string]$Branch)
    Join-Path $RepoRoot "specs/$Branch"
}

function Find-FeatureDirByPrefix {
    param([string]$RepoRoot, [string]$Branch)

    $specsDir = Join-Path $RepoRoot "specs"

    # If branch doesn't have numeric prefix, fall back to exact match
    if ($Branch -notmatch '^(\d{3})-') {
        return (Join-Path $specsDir $Branch)
    }

    $prefix = $matches[1]

    # Search for directories in specs/ that start with this prefix
    $dirs = @()
    if (Test-Path $specsDir) {
        $dirs = Get-ChildItem -Path $specsDir -Directory -Filter "$prefix-*" -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty Name
    }

    # Handle results
    if (-not $dirs -or $dirs.Count -eq 0) {
        # No match found - return the branch name path (will fail later with clear error)
        return (Join-Path $specsDir $Branch)
    }

    if ($dirs.Count -eq 1) {
        # Exactly one match - perfect!
        return (Join-Path $specsDir $dirs[0])
    }

    # Multiple matches - this shouldn't happen with proper naming convention
    Write-Warning "ERROR: Multiple spec directories found with prefix '$prefix': $($dirs -join ', ')"
    Write-Warning "Please ensure only one spec directory exists per numeric prefix."
    return (Join-Path $specsDir $Branch)
}

function Get-FeaturePathsEnv {
    $repoRoot = Get-RepoRoot
    $currentBranch = Get-CurrentBranch
    $hasGit = Test-HasGit
    # Use prefix-based lookup to support multiple branches per spec
    $featureDir = Find-FeatureDirByPrefix -RepoRoot $repoRoot -Branch $currentBranch
    
    [PSCustomObject]@{
        REPO_ROOT     = $repoRoot
        CURRENT_BRANCH = $currentBranch
        BRANCH        = $currentBranch
        HAS_GIT       = $hasGit
        FEATURE_DIR   = $featureDir
        FEATURE_SPEC  = Join-Path $featureDir 'spec.md'
        IMPL_PLAN     = Join-Path $featureDir 'plan.md'
        TASKS         = Join-Path $featureDir 'tasks.md'
        RESEARCH      = Join-Path $featureDir 'research.md'
        DATA_MODEL    = Join-Path $featureDir 'data-model.md'
        QUICKSTART    = Join-Path $featureDir 'quickstart.md'
        CONTRACTS_DIR = Join-Path $featureDir 'contracts'
    }
}

function Resolve-InputFileAbs {
    param(
        [Parameter(Mandatory=$true)]
        [string]$RepoRoot,
        [Parameter(Mandatory=$true)]
        [string]$InputFile
    )

    if ([string]::IsNullOrWhiteSpace($InputFile)) {
        throw 'ERROR: input file is required'
    }

    $candidate = if ([System.IO.Path]::IsPathRooted($InputFile)) {
        $InputFile
    } else {
        Join-Path $RepoRoot $InputFile
    }

    $parent = Split-Path -Parent $candidate
    if (-not (Test-Path $parent -PathType Container)) {
        throw "ERROR: Input file parent directory does not exist: $parent"
    }

    return (Join-Path (Resolve-Path $parent).Path (Split-Path -Leaf $candidate))
}

function Resolve-FeatureDirFromInputFile {
    param(
        [Parameter(Mandatory=$true)]
        [string]$RepoRoot,
        [Parameter(Mandatory=$true)]
        [string]$InputFileAbs
    )

    if (-not (Test-Path $InputFileAbs -PathType Leaf)) {
        throw "ERROR: Input file does not exist: $InputFileAbs"
    }

    $specsRoot = (Join-Path $RepoRoot 'specs') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $InputFileAbs.StartsWith($specsRoot)) {
        throw "ERROR: Input file must be under specs/<feature>/: $InputFileAbs"
    }

    $featureDir = Split-Path -Parent $InputFileAbs
    if (-not $featureDir.StartsWith($specsRoot)) {
        throw "ERROR: Failed to derive feature directory from input file: $InputFileAbs"
    }

    return $featureDir
}

function Test-InputFileForMode {
    param(
        [Parameter(Mandatory=$false)]
        [string]$Mode,
        [Parameter(Mandatory=$true)]
        [string]$InputFileAbs
    )

    $basename = Split-Path -Leaf $InputFileAbs

    switch ($Mode) {
        '' { return $true }
        'generic' { return $true }
        'plan' {
            if ($basename -ne 'spec.md') { throw "ERROR: Mode 'plan' requires input basename 'spec.md', got '$basename'" }
            return $true
        }
        'design' {
            if ($basename -ne 'spec.md') { throw "ERROR: Mode 'design' requires input basename 'spec.md', got '$basename'" }
            return $true
        }
        'tasks' {
            if ($basename -ne 'plan.md') { throw "ERROR: Mode 'tasks' requires input basename 'plan.md', got '$basename'" }
            return $true
        }
        'agent_context' {
            if ($basename -ne 'plan.md') { throw "ERROR: Mode 'agent_context' requires input basename 'plan.md', got '$basename'" }
            return $true
        }
        'preview' {
            if ($basename -notin @('spec.md','plan.md','tasks.md')) {
                throw "ERROR: Mode 'preview' requires input basename spec.md|plan.md|tasks.md, got '$basename'"
            }
            return $true
        }
        'analyze' {
            if ($basename -notin @('plan.md','tasks.md')) {
                throw "ERROR: Mode 'analyze' requires input basename plan.md|tasks.md, got '$basename'"
            }
            return $true
        }
        'implement' {
            if ($basename -ne 'tasks.md') { throw "ERROR: Mode 'implement' requires input basename 'tasks.md', got '$basename'" }
            return $true
        }
        default {
            throw "ERROR: Unknown mode '$Mode'"
        }
    }
}

function Get-FeaturePathsFromInputFile {
    param(
        [Parameter(Mandatory=$true)]
        [string]$InputFile,
        [Parameter(Mandatory=$false)]
        [string]$Mode
    )

    $repoRoot = Get-RepoRoot
    $hasGit = Test-HasGit
    $inputFileAbs = Resolve-InputFileAbs -RepoRoot $repoRoot -InputFile $InputFile
    $featureDir = Resolve-FeatureDirFromInputFile -RepoRoot $repoRoot -InputFileAbs $inputFileAbs
    Test-InputFileForMode -Mode $Mode -InputFileAbs $inputFileAbs | Out-Null

    $featureName = Split-Path -Leaf $featureDir

    [PSCustomObject]@{
        REPO_ROOT      = $repoRoot
        CURRENT_BRANCH = $featureName
        BRANCH         = $featureName
        HAS_GIT        = $hasGit
        INPUT_FILE     = $InputFile
        INPUT_FILE_ABS = $inputFileAbs
        INPUT_BASENAME = (Split-Path -Leaf $inputFileAbs)
        FEATURE_DIR    = $featureDir
        FEATURE_SPEC   = Join-Path $featureDir 'spec.md'
        IMPL_PLAN      = Join-Path $featureDir 'plan.md'
        TASKS          = Join-Path $featureDir 'tasks.md'
        RESEARCH       = Join-Path $featureDir 'research.md'
        DATA_MODEL     = Join-Path $featureDir 'data-model.md'
        QUICKSTART     = Join-Path $featureDir 'quickstart.md'
        CONTRACTS_DIR  = Join-Path $featureDir 'contracts'
    }
}

function Test-FileExists {
    param([string]$Path, [string]$Description)
    if (Test-Path -Path $Path -PathType Leaf) {
        Write-Output "  ✓ $Description"
        return $true
    } else {
        Write-Output "  ✗ $Description"
        return $false
    }
}

function Test-DirHasFiles {
    param([string]$Path, [string]$Description)
    if ((Test-Path -Path $Path -PathType Container) -and (Get-ChildItem -Path $Path -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer } | Select-Object -First 1)) {
        Write-Output "  ✓ $Description"
        return $true
    } else {
        Write-Output "  ✗ $Description"
        return $false
    }
}
