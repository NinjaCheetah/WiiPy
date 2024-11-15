# Build.ps1 for WiiPy

# Default option is to run build, like a Makefile
param(
    [string]$Task = "build"
)

$buildWiiPy = {
    Write-Host "Building WiiPy..."
    python -m nuitka --show-progress --assume-yes-for-downloads --onefile wiipy.py --onefile-tempdir-spec="{CACHE_DIR}/NinjaCheetah/WiiPy"
}

$cleanWiiPy = {
    Write-Host "Cleaning..."
    Remove-Item -Recurse -Force wiipy.exe, ./wiipy.build/, ./wiipy.dist/, ./wiipy.onefile-build/
}

switch ($Task.ToLower()) {
    "build" {
        & $buildWiiPy
        break
    }
    "clean" {
        & $cleanWiiPy
        break
    }
    default {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Write-Host "Available tasks: build, clean"
        break
    }
}
