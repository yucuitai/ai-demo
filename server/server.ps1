# 博客智能体 - 后端 API 服务器
# PowerShell HttpListener 实现，无需安装 Node.js 或 Python

$port = 3000
$root = Split-Path $PSScriptRoot -Parent
$clientDir = Join-Path $root "client"
$dataDir = Join-Path $PSScriptRoot "data"
$uploadDir = Join-Path $dataDir "uploads"
$hotspotsFile = Join-Path $dataDir "hotspots.json"

if (-not (Test-Path $uploadDir)) { New-Item -ItemType Directory -Force -Path $uploadDir | Out-Null }

# 初始化热点数据
if (-not (Test-Path $hotspotsFile)) {
    $initData = @(
        @{ id="1";  title="AI大模型最新进展：GPT-5发布时间曝光";      content="OpenAI即将发布新一代大模型，性能提升显著，多模态能力大幅增强，业界高度关注";          hotValue=98765; type="tech";         time="2小时前" },
        @{ id="2";  title="2025年最值得关注的10个AI工具";              content="从文本生成到视频制作，这些AI工具正在改变我们的工作方式，提升创作效率";                    hotValue=87654; type="tech";         time="3小时前" },
        @{ id="3";  title="远程办公成为主流：如何保持高效工作";        content="后疫情时代，越来越多的企业采用混合办公模式，如何平衡工作与生活成为新课题";              hotValue=76543; type="career";       time="5小时前" },
        @{ id="4";  title="健康生活新趋势：植物性饮食的科学依据";      content="越来越多的研究表明，植物性饮食对健康有诸多益处，全球掀起绿色饮食潮流";                  hotValue=65432; type="life";         time="6小时前" },
        @{ id="5";  title="年度大片票房破纪录：国产电影崛起";          content="今年春节档电影票房再创新高，多部国产佳作获得口碑票房双丰收，文化自信不断增强";          hotValue=54321; type="entertainment"; time="8小时前" },
        @{ id="6";  title="程序员职业发展：从初级到架构师的成长之路";  content="分享10年编程经验，聊聊技术成长路上的那些坑与收获，给年轻开发者一些借鉴";                hotValue=43210; type="career";       time="10小时前" },
        @{ id="7";  title="智能家居全面普及：你家升级了吗？";          content="从智能音箱到全屋智能，智能家居正在走进千家万户，生活变得更便捷更舒适";                  hotValue=32109; type="tech";         time="12小时前" },
        @{ id="8";  title="断舍离生活方式：极简主义的艺术";            content="通过整理物品来整理内心，极简主义生活带来的改变远超想象，越来越多年轻人开始践行";          hotValue=21098; type="life";         time="1天前" },
        @{ id="9";  title="新能源汽车价格战：消费者迎来购车好时机";    content="各大车企纷纷降价促销，新能源汽车市场竞争白热化，消费者选择空间前所未有";                hotValue=45678; type="tech";         time="4小时前" },
        @{ id="10"; title="面试技巧大揭秘：大厂面试官亲述";             content="资深面试官分享面试中的关键考察点，如何在众多候选人中脱颖而出";                          hotValue=38901; type="career";       time="7小时前" },
        @{ id="11"; title="城市露营风潮：都市人的诗意栖息";            content="无需远行就能感受自然，城市露营成为年轻人休闲新宠，重新定义都市生活方式";                hotValue=29876; type="life";         time="9小时前" },
        @{ id="12"; title="热门综艺背后的制作故事";                     content="综艺节目如何制造话题与热度？揭秘综艺制作的幕后团队和创意过程";                          hotValue=18765; type="entertainment"; time="11小时前" }
    )
    $initData | ConvertTo-Json -Depth 10 | Out-File $hotspotsFile -Encoding UTF8
}

$mimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".js"   = "application/javascript; charset=utf-8"
    ".css"  = "text/css; charset=utf-8"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".jpeg" = "image/jpeg"
    ".gif"  = "image/gif"
    ".webp" = "image/webp"
    ".svg"  = "image/svg+xml"
    ".ico"  = "image/x-icon"
    ".json" = "application/json; charset=utf-8"
    ".woff" = "font/woff"
    ".woff2"= "font/woff2"
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Prefixes.Add("http://127.0.0.1:$port/")
$listener.Start()

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  博客智能体 - API 服务器已启动" -ForegroundColor Green
Write-Host "  前端: http://localhost:$port" -ForegroundColor Yellow
Write-Host "  API:  http://localhost:$port/api" -ForegroundColor Yellow
Write-Host "  按 Ctrl+C 停止服务器" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

function ReadRequestBody($request) {
    $body = $null
    if ($request.HasEntityBody) {
        $reader = New-Object System.IO.StreamReader($request.InputStream, $request.ContentEncoding)
        $body = $reader.ReadToEnd()
        $reader.Close()
    }
    return $body
}

function SendJson($response, $data, $statusCode = 200) {
    $response.StatusCode = $statusCode
    $response.ContentType = "application/json; charset=utf-8"
    $json = if ($data -is [string]) { $data } else { $data | ConvertTo-Json -Depth 10 -Compress }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $response.ContentLength64 = $bytes.Length
    $response.OutputStream.Write($bytes, 0, $bytes.Length)
}

function SendError($response, $message, $statusCode = 400) {
    SendJson $response @{ error = $message } $statusCode
}

function AddCorsHeaders($response) {
    $response.Headers.Add("Access-Control-Allow-Origin", "*")
    $response.Headers.Add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    $response.Headers.Add("Access-Control-Allow-Headers", "Content-Type, Authorization")
}

function ServeStaticFile($path, $response) {
    $cleanPath = $path.TrimStart('/')
    if ($cleanPath -eq '' -or $cleanPath.EndsWith('/')) { $cleanPath = 'index.html' }
    $filePath = Join-Path $clientDir $cleanPath

    if (Test-Path $filePath -PathType Leaf) {
        $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
        $contentType = if ($mimeTypes.ContainsKey($ext)) { $mimeTypes[$ext] } else { "application/octet-stream" }
        $response.ContentType = $contentType
        $buffer = [System.IO.File]::ReadAllBytes($filePath)
        $response.ContentLength64 = $buffer.Length
        $response.OutputStream.Write($buffer, 0, $buffer.Length)
        return $true
    }
    return $false
}

function ParseMultipartFormData($request) {
    $contentType = $request.ContentType
    if (-not $contentType -or -not $contentType.Contains("multipart/form-data")) { return @{ fields = @{}; files = @() } }

    $boundary = "--" + ($contentType -split "boundary=")[1].Trim('"')
    $bodyBytes = New-Object System.IO.MemoryStream
    $request.InputStream.CopyTo($bodyBytes)
    $bodyBytes.Position = 0
    $reader = New-Object System.IO.StreamReader($bodyBytes)
    $bodyText = $reader.ReadToEnd()
    $reader.Close()
    $bodyBytes.Position = 0

    $fields = @{}
    $files = @()

    $parts = $bodyText -split [regex]::Escape($boundary)
    foreach ($part in $parts) {
        if ($part.Trim() -eq '' -or $part.Trim() -eq '--') { continue }

        $headerEnd = $part.IndexOf("`r`n`r`n")
        if ($headerEnd -eq -1) { $headerEnd = $part.IndexOf("`n`n") }

        if ($headerEnd -gt 0) {
            $headerSection = $part.Substring(0, $headerEnd)
            $bodyStart = $headerEnd
            if ($part[$bodyStart] -eq "`r") { $bodyStart += 2 } else { $bodyStart += 2 }

            $bodyContent = $part.Substring($bodyStart)
            if ($bodyContent.EndsWith("`r`n")) { $bodyContent = $bodyContent.Substring(0, $bodyContent.Length - 2) }
            elseif ($bodyContent.EndsWith("`n")) { $bodyContent = $bodyContent.Substring(0, $bodyContent.Length - 1) }

            if ($headerSection -match 'name="([^"]+)"') {
                $name = $Matches[1]
                if ($headerSection -match 'filename="([^"]+)"') {
                    $filename = $Matches[1]

                    $bytes = $bodyBytes.ToArray()
                    $headerBytes = [System.Text.Encoding]::UTF8.GetBytes($headerSection + "`r`n`r`n")
                    $contentStart = 0
                    for ($k = 0; $k -lt $bytes.Length - $headerBytes.Length; $k++) {
                        $match = $true
                        for ($j = 0; $j -lt $headerBytes.Length; $j++) {
                            if ($bytes[$k + $j] -ne $headerBytes[$j]) { $match = $false; break }
                        }
                        if ($match) { $contentStart = $k + $headerBytes.Length; break }
                    }

                    if ($contentStart -gt 0) {
                        $contentLength = $bodyContent.Length
                        while ($contentLength -gt 0 -and $bytes[$contentStart + $contentLength - 1] -eq 10) { $contentLength-- }
                        while ($contentLength -gt 0 -and $bytes[$contentStart + $contentLength - 1] -eq 13) { $contentLength-- }

                        $filePath = Join-Path $uploadDir $filename
                        $fileStream = [System.IO.File]::Create($filePath)
                        $fileStream.Write($bytes, $contentStart, $contentLength)
                        $fileStream.Close()

                        $files += @{
                            name = $name
                            filename = $filename
                            path = $filePath
                            url = "/api/uploads/$filename"
                        }
                    }
                }
                else {
                    $fields[$name] = $bodyContent
                }
            }
        }
    }

    $bodyBytes.Close()
    return @{ fields = $fields; files = $files }
}

# ── 热点数据管理 ──

function GetHotspots($type, $search, $page, $pageSize) {
    $all = Get-Content $hotspotsFile -Encoding UTF8 | ConvertFrom-Json | ForEach-Object {
        [PSCustomObject]@{ id=$_.id; title=$_.title; content=$_.content; hotValue=$_.hotValue; type=$_.type; time=$_.time }
    }

    if ($type -and $type -ne 'all') { $all = $all | Where-Object { $_.type -eq $type } }
    if ($search) { 
        $q = $search.ToLower()
        $all = $all | Where-Object { $_.title.ToLower().Contains($q) -or $_.content.ToLower().Contains($q) }
    }

    $total = @($all).Count
    $start = ($page - 1) * $pageSize
    $items = $all | Select-Object -Skip $start -First $pageSize

    return @{ items = @($items); total = $total; page = $page; pageSize = $pageSize }
}

# ── 博客内容生成 ──

function GenerateBlogContent($topics, $style, $wordCount, $depth) {
    $topicTitles = ($topics | ForEach-Object { $_.title }) -join '、'
    $topicContent = ($topics | ForEach-Object { $_.content }) -join '。'

    $styleMap = @{
        professional  = @{ tone="严谨专业、逻辑清晰"; intro="深入剖析"; prefix="从专业视角审视" }
        casual        = @{ tone="轻松活泼、通俗易懂"; intro="聊聊"; prefix="今天咱们来聊聊" }
        educational   = @{ tone="干货满满、知识性强"; intro="科普"; prefix="本篇文章带你全面了解" }
        emotional     = @{ tone="温暖真诚、有共鸣感"; intro="感悟"; prefix="让我们一同感受" }
    }
    $st = if ($styleMap[$style]) { $styleMap[$style] } else { $styleMap['professional'] }

    $depthMap = @{
        basic = @{ sections=2; depthLabel="基础简述"; analysis="从表面现象入手" }
        deep  = @{ sections=3; depthLabel="深度解析"; analysis="深入剖析背后逻辑与影响" }
    }
    $dp = if ($depthMap[$depth]) { $depthMap[$depth] } else { $depthMap['deep'] }

    $wordRanges = @{ short="300-500"; standard="800-1200"; long="1500-2000" }
    $wc = if ($wordRanges[$wordCount]) { $wordRanges[$wordCount] } else { "800-1200" }

    $blogContent = @{
        title = "$topicTitles：$($st.prefix)前沿话题"
        subtitle = "基于$($dp.depthLabel) | $($st.tone) | 目标字数：${wc}字"
        introduction = "在这个信息爆炸的时代，$topicTitles 等话题持续占据热搜榜单，引发了社会各界的广泛关注和讨论。$($dp.analysis)，我们或许能从中发现时代的脉搏和未来的方向。每一个热点背后，都折射出大众的关注焦点与价值取向。"
        sections = @()
        conclusion = "综上所述，$topicTitles 不仅是当下热议的话题，更代表了社会发展的某种趋势。我们应当保持开放的心态，在关注热点的同时，也要有自己的独立思考。希望本文能为你提供有价值的参考，激发更多的思考与讨论。"
    }

    $sectionTemplates = @(
        @{ heading="热点背景与现状"; template="当前，{0}已成为备受瞩目的热点话题。随着信息传播速度的加快，这些话题迅速进入公众视野，引发了广泛讨论。从社交媒体到主流新闻，从线下交流到线上互动，这些热点正在以一种前所未有的方式影响着人们的思考和行为方式。" },
        @{ heading="核心要素分析"; template="深入探究{0}，我们可以从以下几个维度理解其重要性：首先，这些热点反映了当前阶段大众最关心的议题；其次，它们往往与技术变革、社会转型或文化演变密切相关；最后，热点的爆发并非偶然，而是多种因素共同作用的结果。" },
        @{ heading="深度解读与思考"; template="从更宏观的角度来看，{0}揭示了更深层次的社会现象。不同立场的观点碰撞，让我们得以从多角度审视同一问题。值得注意的是，在信息高度碎片化的今天，保持理性判断尤为关键。我们既要关注热点的表面信息，更要洞察其背后的本质。" }
    )

    $numSections = $dp.sections
    for ($i = 0; $i -lt $numSections; $i++) {
        $sec = $sectionTemplates[$i]
        $blogContent.sections += @{ heading = $sec.heading; content = ($sec.template -f $topicTitles) }
    }

    if ($wordCount -eq 'long') {
        $blogContent.sections += @{
            heading = "延伸阅读与观点碰撞"
            content = "除了上述分析，我们还关注到业内专家学者对此话题的多元解读。有观点认为，$topicTitles 所代表的趋势将持续深化；也有声音指出，我们需要警惕其中可能存在的泡沫和过度炒作。无论如何，保持学习和思辨的心态，是应对变化的最佳策略。"
        }
    }

    $blogContent.introduction = if ($wordCount -eq 'short') { 
        "$topicTitles 成为近期热门话题，引发了广泛关注。$($dp.analysis)。"
    } else { $blogContent.introduction }

    return $blogContent
}

# ── 图片生成 ──

function GenerateImages($keyword, $style, $width, $height, $count) {
    $images = @()
    $timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

    $styleColors = @{
        realistic      = @("2c3e50", "34495e", "7f8c8d")
        illustration   = @("e74c3c", "3498db", "f39c12")
        minimal        = @("ecf0f1", "bdc3c7", "95a5a6")
        tech           = @("1a1a2e", "16213e", "0f3460")
    }
    $colors = if ($styleColors[$style]) { $styleColors[$style] } else { $styleColors['realistic'] }

    for ($i = 0; $i -lt $count; $i++) {
        $seed = $timestamp + $i
        $bg = $colors[$i % $colors.Count]
        $url = "https://picsum.photos/seed/$seed/$width/$height"
        
        $images += @{
            id = "img_$($timestamp)_$i"
            url = $url
            width = $width
            height = $height
            style = $style
            placeholder = "https://via.placeholder.com/${width}x${height}/$bg/ffffff?text=" + [uri]::EscapeDataString($keyword.Substring(0, [Math]::Min(6, $keyword.Length)))
        }
    }
    return $images
}

# ── 主循环 ──

while ($listener.IsListening) {
    try {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        AddCorsHeaders $response
        
        $path = $request.Url.LocalPath
        $method = $request.HttpMethod
        $queryString = $request.Url.Query

        $time = Get-Date -Format 'HH:mm:ss'

        # 处理 OPTIONS（CORS 预检）
        if ($method -eq 'OPTIONS') {
            $response.StatusCode = 204
            $response.Close()
            Write-Host "$time [204] OPTIONS $path" -ForegroundColor Gray
            continue
        }

        # ── API 路由 ──

        if ($path -eq '/api/hotspots' -and $method -eq 'GET') {
            $query = [System.Web.HttpUtility]::ParseQueryString($queryString)
            $type = $query['type']
            $search = $query['search']
            $page = if ($query['page']) { [int]$query['page'] } else { 1 }
            $pageSize = if ($query['pageSize']) { [int]$query['pageSize'] } else { 12 }

            $result = GetHotspots $type $search $page $pageSize
            SendJson $response $result
            Write-Host "$time [200] GET $path" -ForegroundColor Green
            $response.Close()
            continue
        }

        if ($path -eq '/api/hotspots/refresh' -and $method -eq 'POST') {
            $all = Get-Content $hotspotsFile -Encoding UTF8 | ConvertFromJson
            foreach ($item in $all) {
                $item.hotValue = [int]$item.hotValue + (Get-Random -Min -5000 -Max 15000)
                $item.hotValue = [Math]::Max(1000, [Math]::Min(99999, $item.hotValue))
            }
            $shuffled = $all | Sort-Object { Get-Random }
            $shuffled | ConvertTo-Json -Depth 10 | Out-File $hotspotsFile -Encoding UTF8

            $result = GetHotspots $null $null 1 12
            SendJson $response $result
            Write-Host "$time [200] POST $path" -ForegroundColor Green
            $response.Close()
            continue
        }

        if ($path -eq '/api/blog/generate' -and $method -eq 'POST') {
            $body = ReadRequestBody $request
            try {
                $data = $body | ConvertFrom-Json
                if (-not $data.topics -or @($data.topics).Count -eq 0) {
                    SendError $response "请选择至少一个热点话题" 400
                }
                else {
                    $result = GenerateBlogContent $data.topics $data.style $data.wordCount $data.depth
                    SendJson $response @{ success = $true; data = $result }
                    Write-Host "$time [200] POST $path" -ForegroundColor Green
                }
            }
            catch {
                SendError $response "请求参数解析失败: $($_.Exception.Message)" 400
                Write-Host "$time [400] POST $path - $($_.Exception.Message)" -ForegroundColor Red
            }
            $response.Close()
            continue
        }

        if ($path -eq '/api/images/generate' -and $method -eq 'POST') {
            $body = ReadRequestBody $request
            try {
                $data = $body | ConvertFrom-Json
                $keyword = if ($data.keyword) { $data.keyword } else { "blog" }
                $style = if ($data.style) { $data.style } else { "realistic" }
                $width = if ($data.width) { [int]$data.width } else { 800 }
                $height = if ($data.height) { [int]$data.height } else { 600 }
                $count = if ($data.count) { [int]$data.count } else { 2 }

                Start-Sleep -Seconds 1
                $result = GenerateImages $keyword $style $width $height $count
                SendJson $response @{ success = $true; data = $result }
                Write-Host "$time [200] POST $path ($count images)" -ForegroundColor Green
            }
            catch {
                SendError $response "图片生成失败: $($_.Exception.Message)" 500
                Write-Host "$time [500] POST $path - $($_.Exception.Message)" -ForegroundColor Red
            }
            $response.Close()
            continue
        }

        if ($path -eq '/api/images/upload' -and $method -eq 'POST') {
            try {
                $parsed = ParseMultipartFormData $request
                if ($parsed.files.Count -eq 0) {
                    SendError $response "未检测到上传文件" 400
                }
                else {
                    $urls = $parsed.files | ForEach-Object { "http://localhost:$port$($_.url)" }
                    SendJson $response @{ success = $true; data = @{ urls = @($urls); files = @($parsed.files) } }
                    Write-Host "$time [200] POST $path ($($parsed.files.Count) files)" -ForegroundColor Green
                }
            }
            catch {
                SendError $response "文件上传失败: $($_.Exception.Message)" 500
                Write-Host "$time [500] POST $path - $($_.Exception.Message)" -ForegroundColor Red
            }
            $response.Close()
            continue
        }

        if ($path.StartsWith('/api/uploads/') -and $method -eq 'GET') {
            $fileName = $path.Substring('/api/uploads/'.Length)
            $filePath = Join-Path $uploadDir $fileName
            if (Test-Path $filePath -PathType Leaf) {
                $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
                $contentType = if ($mimeTypes.ContainsKey($ext)) { $mimeTypes[$ext] } else { "application/octet-stream" }
                $response.ContentType = $contentType
                $buffer = [System.IO.File]::ReadAllBytes($filePath)
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
                Write-Host "$time [200] GET $path" -ForegroundColor Green
            }
            else {
                SendError $response "文件不存在" 404
                Write-Host "$time [404] GET $path" -ForegroundColor Red
            }
            $response.Close()
            continue
        }

        # ── 静态文件服务（前端） ── 
        if ($method -eq 'GET') {
            if (ServeStaticFile $path $response) {
                Write-Host "$time [200] $path" -ForegroundColor Green
            }
            else {
                SendError $response "404 - Not Found" 404
                Write-Host "$time [404] $path" -ForegroundColor Red
            }
            $response.Close()
            continue
        }

        SendError $response "Method Not Allowed" 405
        Write-Host "$time [405] $method $path" -ForegroundColor Yellow
        $response.Close()
    }
    catch {
        try { $response.Close() } catch {}
        Write-Host "$time [ERR] $($_.Exception.Message)" -ForegroundColor Red
    }
}
