# Build.ps1 for clean FSDiary

# Default option is to run build, like a Makefile
param(
    [string]$Task = "build"
)

$buildFSDiary = {
    Write-Host "正在打包FSDiary..."
    python -m nuitka --show-progress --assume-yes-for-downloads app.py
}

$cleanFSDiary = {
    Write-Host "Cleaning..."
    Remove-Item -Recurse -Force app.exe, ./app.build/, ./app.dist/, ./app.onefile-build/ ,/build/ ,/dist/ ,FSDiary.spec
}

switch ($Task.ToLower()) {
    "build" {
        & $buildFSDiary
        break
    }
    "clean" {
        & $cleanFSDiary
        break
    }
    default {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Write-Host "Available tasks: build, clean"
        break
    }
}