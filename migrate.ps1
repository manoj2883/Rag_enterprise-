# Antigravity Conversation & Codebase Migration Utility
# This script bundles the codebase and the entire conversation history/logs
# into a single ZIP package for easy migration to your other account.

$ErrorActionPreference = "Stop"

# Define source directories
$codebaseDir = "C:\Users\Manoj Kumar\.gemini\antigravity\scratch\Rag_enterprise-"
$brainDir = "C:\Users\Manoj Kumar\.gemini\antigravity\brain\55afe6a7-a245-43b0-94c3-f1987878d765"
$desktopPath = [System.IO.Path]::Combine([Environment]::GetFolderPath("Desktop"), "Antigravity_Migration_Package")
$zipPath = "$desktopPath.zip"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Antigravity Conversation & Codebase Migration Utility  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if directories exist
if (-not (Test-Path $codebaseDir)) {
    Write-Error "Codebase directory not found at: $codebaseDir"
}
if (-not (Test-Path $brainDir)) {
    Write-Error "Conversation brain directory not found at: $brainDir"
}

# Create temp staging folder on Desktop
if (Test-Path $desktopPath) {
    Remove-Item -Path $desktopPath -Recurse -Force
}
New-Item -ItemType Directory -Path $desktopPath | Out-Null

Write-Host "[1/3] Copying codebase (excluding large venv directory)..." -ForegroundColor Yellow
$null = New-Item -ItemType Directory -Path "$desktopPath\codebase"
# Copy codebase files, excluding 'venv' and '.git' to keep package lightweight
Get-ChildItem -Path $codebaseDir -Exclude "venv", ".git" | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination "$desktopPath\codebase\" -Recurse -Force
}

Write-Host "[2/3] Copying conversation history, plans, and logs..." -ForegroundColor Yellow
$null = New-Item -ItemType Directory -Path "$desktopPath\brain_history"
Copy-Item -Path "$brainDir\*" -Destination "$desktopPath\brain_history\" -Recurse -Force

Write-Host "[3/3] Creating migration ZIP archive on your Desktop..." -ForegroundColor Yellow
if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}
Compress-Archive -Path "$desktopPath\*" -DestinationPath $zipPath -Force

# Clean up temp directory
Remove-Item -Path $desktopPath -Recurse -Force

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " SUCCESS: Migration package created successfully!" -ForegroundColor Green
Write-Host " Package location: $zipPath" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "HOW TO RESTORE IN YOUR NEW ACCOUNT:" -ForegroundColor Cyan
Write-Host "1. Start a new chat session in your new Antigravity account." -ForegroundColor White
Write-Host "2. Find the new conversation ID (it will show in your prompt or directory structure)." -ForegroundColor White
Write-Host "3. Unzip the package." -ForegroundColor White
Write-Host "4. Copy the files from 'codebase' folder to your new active workspace." -ForegroundColor White
Write-Host "5. Copy all files and folders inside 'brain_history' to the new conversation folder" -ForegroundColor White
Write-Host "   at C:\Users\Manoj Kumar\.gemini\antigravity\brain\<NEW-CONVERSATION-ID>\" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
