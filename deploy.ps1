# 博客智能体 - GitHub 一键部署脚本
# 自动安装 Git（如需要）、初始化仓库、推送到 GitHub

param(
    [string]$RepoName = "blog-agent",
    [string]$Username = "",
    [string]$Token = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  博客智能体 - GitHub 部署工具" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# —— 1. 检查/安装 Git ——
$gitExe = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitExe) {
    Write-Host "[1/5] Git 未安装，正在自动安装..." -ForegroundColor Yellow
    
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.45.1.windows.1/PortableGit-2.45.1-64-bit.7z.exe"
    $gitInstaller = "$env:TEMP\PortableGit.exe"
    
    Write-Host "  下载 Git Portable..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller -UseBasicParsing
    
    $gitDir = "C:\Program Files\Git"
    Write-Host "  安装到 $gitDir ..." -ForegroundColor Gray
    Start-Process -FilePath $gitInstaller -ArgumentList "-o$gitDir -y" -Wait -NoNewWindow
    Remove-Item $gitInstaller -Force
    
    $env:Path = "$gitDir\bin;$env:Path"
    Write-Host "  Git 安装完成！" -ForegroundColor Green
}
else {
    Write-Host "[1/5] Git 已就绪: $(git --version)" -ForegroundColor Green
}

# —— 2. 收集 GitHub 信息 ——
if (-not $Username) {
    $Username = Read-Host "请输入 GitHub 用户名"
}
if (-not $Token) {
    Write-Host ""
    Write-Host "需要 GitHub Personal Access Token (classic)" -ForegroundColor Yellow
    Write-Host "获取方式: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)" -ForegroundColor Gray
    Write-Host "权限: repo (全部) + workflow (可选)" -ForegroundColor Gray
    Write-Host ""
    $Token = Read-Host "请输入 GitHub Token"
}

if (-not $Username -or -not $Token) {
    Write-Host "用户名和 Token 不能为空！" -ForegroundColor Red
    exit 1
}

$RepoName = Read-Host "仓库名称 (默认: blog-agent)"
if (-not $RepoName) { $RepoName = "blog-agent" }

# —— 3. 初始化 Git 仓库 ——
Write-Host "[2/5] 初始化 Git 仓库..." -ForegroundColor Cyan

if (Test-Path ".git") {
    Write-Host "  已存在 .git 目录，跳过初始化" -ForegroundColor Gray
}
else {
    git init
    Write-Host "  Git 仓库初始化完成" -ForegroundColor Green
}

# 配置用户信息
$gitUser = git config user.name
if (-not $gitUser) {
    git config user.name $Username
    git config user.email "$Username@users.noreply.github.com"
}

# —— 4. 添加文件并提交 ——
Write-Host "[3/5] 添加文件..." -ForegroundColor Cyan
git add .

Write-Host "[4/5] 创建提交..." -ForegroundColor Cyan
$commitMsg = "初始化博客智能体项目 - 前后端分离架构"
git commit -m $commitMsg 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    # 如果没有变更，尝试 amend
    git commit --allow-empty -m $commitMsg
}
Write-Host "  提交完成: $commitMsg" -ForegroundColor Green

# —— 5. 推送到 GitHub ——
Write-Host "[5/5] 推送到 GitHub..." -ForegroundColor Cyan

$remoteUrl = "https://$Username`:$Token@github.com/$Username/$RepoName.git"

# 检查远程仓库是否已存在
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    git remote set-url origin $remoteUrl
}
else {
    git remote add origin $remoteUrl
}

# 尝试推送到 main 分支
$pushSuccess = $false
try {
    git push -u origin main 2>&1
    if ($LASTEXITCODE -eq 0) { $pushSuccess = $true }
}
catch { }

if (-not $pushSuccess) {
    try {
        git push -u origin master 2>&1
        if ($LASTEXITCODE -eq 0) { $pushSuccess = $true }
    }
    catch { }
}

if (-not $pushSuccess) {
    Write-Host ""
    Write-Host "推送失败！可能原因:" -ForegroundColor Red
    Write-Host "  1. 仓库 '$RepoName' 不存在于 GitHub" -ForegroundColor Yellow
    Write-Host "  2. Token 权限不足" -ForegroundColor Yellow
    Write-Host "  3. 网络连接问题" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "手动创建仓库:" -ForegroundColor Green
    Write-Host "  https://github.com/new" -ForegroundColor Gray
    Write-Host "  仓库名称: $RepoName" -ForegroundColor Gray
    Write-Host "  必须为空仓库（不要勾选 README/.gitignore）" -ForegroundColor Gray
    Write-Host ""
    Write-Host "然后重新运行此脚本" -ForegroundColor Gray
    exit 1
}

# 清理 token
git remote set-url origin "https://github.com/$Username/$RepoName.git"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署成功！" -ForegroundColor Green
Write-Host "  仓库地址: https://github.com/$Username/$RepoName" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
