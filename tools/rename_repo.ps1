[CmdletBinding()]
param(
    [bool]$DryRun = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Action {
    param(
        [string]$Message
    )
    Write-Host "[rename] $Message"
}

$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    throw 'Unable to locate git repository root.'
}
Set-Location $repoRoot

$renameMap = @(
    @{ Old = 'AGENT.md'; New = 'AGENT.hub.md' },
    @{ Old = 'docs/agents/AGENT.md'; New = 'docs/agents/AGENT.index.md' },
    @{ Old = 'docs/agents/README.md'; New = 'docs/agents/AGENTS.readme.md' },
    @{ Old = 'docs/roadmap/_template_step.md'; New = 'docs/roadmap/ROADMAP.template-step.md' },
    @{ Old = 'docs/roadmap/README.md'; New = 'docs/roadmap/ROADMAP.readme.md' },
    @{ Old = 'README.md'; New = 'PROJECT.readme.md' }
)

$gitCmd = Get-Command git -ErrorAction SilentlyContinue

foreach ($entry in $renameMap) {
    $oldPath = Join-Path $repoRoot $entry.Old
    $newPath = Join-Path $repoRoot $entry.New

    if (-not (Test-Path -LiteralPath $oldPath)) {
        Write-Action "Skip (not found): $($entry.Old)"
        continue
    }

    Write-Action "Rename: $($entry.Old) -> $($entry.New)"
    if (-not $DryRun) {
        $newParent = Split-Path -Parent $newPath
        if (-not (Test-Path -LiteralPath $newParent)) {
            New-Item -ItemType Directory -Path $newParent -Force | Out-Null
        }

        if ($gitCmd) {
            git mv --force -- $entry.Old $entry.New | Out-Null
        }
        else {
            Move-Item -LiteralPath $oldPath -Destination $newPath -Force
        }
    }
}

$globalReplacements = [ordered]@{
    'docs/agents/AGENT.md' = 'docs/agents/AGENT.index.md'
    'docs/agents/README.md' = 'docs/agents/AGENTS.readme.md'
    '_template_step.md' = 'docs/roadmap/ROADMAP.template-step.md'
    'docs/roadmap/README.md' = 'docs/roadmap/ROADMAP.readme.md'
    'AGENT.md' = 'AGENT.hub.md'
}

$agentDir = Join-Path $repoRoot 'docs/agents'
$mdFiles = Get-ChildItem -Path $repoRoot -Filter '*.md' -Recurse

foreach ($file in $mdFiles) {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    $updated = $content

    $isAgentFile = $file.FullName.StartsWith($agentDir, [System.StringComparison]::OrdinalIgnoreCase)

    if ($isAgentFile) {
        $updated = $updated.Replace('../AGENT.md', '../../AGENT.hub.md')
        $updated = $updated.Replace('](./AGENT.md', '](./AGENT.index.md')
        $updated = $updated.Replace('](AGENT.md', '](AGENT.index.md')
        $updated = $updated.Replace('(AGENT.md)', '(AGENT.index.md)')
        $updated = $updated.Replace('[AGENT index](AGENT.md', '[AGENT index](AGENT.index.md')
    }

    foreach ($key in $globalReplacements.Keys) {
        $updated = $updated.Replace($key, $globalReplacements[$key])
    }

    if ($updated -ne $content) {
        Write-Action "Update links: $($file.FullName.Substring($repoRoot.Length + 1))"
        if (-not $DryRun) {
            Set-Content -LiteralPath $file.FullName -Value $updated -NoNewline
        }
    }
}

$agentHeaders = @(
    @{ Path = 'docs/agents/AGENT.backend.md'; Lines = @(
        'SUT: docs/specs/spec-fonctionnelle-v0.1.md',
        'Les schemas, services et regles metier doivent respecter les modules et workflows de la spec.'
    ) },
    @{ Path = 'docs/agents/AGENT.frontend.md'; Lines = @(
        'SUT: docs/specs/spec-fonctionnelle-v0.1.md',
        'Les vues (planning, paie, materiel, notifications) et interactions (drag-drop, timeline) suivent la spec.'
    ) },
    @{ Path = 'docs/agents/AGENT.devops.md'; Lines = @(
        'SUT: docs/specs/spec-fonctionnelle-v0.1.md',
        'Les guards/CI verifient la presence et la reference de la spec.'
    ) },
    @{ Path = 'docs/agents/AGENT.docs.md'; Lines = @(
        'SUT: docs/specs/spec-fonctionnelle-v0.1.md',
        'Tous les documents generes doivent rester alignes avec la spec.'
    ) }
)

foreach ($agent in $agentHeaders) {
    $agentPath = Join-Path $repoRoot $agent.Path
    if (-not (Test-Path -LiteralPath $agentPath)) {
        Write-Action "Skip SUT (missing file): $($agent.Path)"
        continue
    }

    $content = Get-Content -LiteralPath $agentPath -Raw
    $needsUpdate = $false
    foreach ($line in $agent.Lines) {
        if (-not ($content.Contains($line))) {
            $needsUpdate = $true
            break
        }
    }

    if ($needsUpdate) {
        Write-Action "Inject SUT header: $($agent.Path)"
        if (-not $DryRun) {
            $prefix = ($agent.Lines -join "`n") + "`n`n"
            Set-Content -LiteralPath $agentPath -Value ($prefix + $content)
        }
    }
    else {
        Write-Action "SUT header present: $($agent.Path)"
    }
}

Write-Action ("DryRun mode: {0}" -f $DryRun)
