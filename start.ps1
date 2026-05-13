# 启动博客智能体服务
$root = Split-Path $PSScriptRoot -Parent
$serverDir = Join-Path $root "server"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  博客智能体 - 启动中..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Set-Location $serverDir

& "C:\Program Files\Python311\python.exe" app.py

Write-Host "服务已停止" -ForegroundColor Yellow
