const API_BASE = '/api';

const state = {
    topics: [],
    selectedTopics: [],
    currentCategory: 'all',
    searchQuery: '',
    blogContent: null,
    images: [],
    imageAlign: 'center',
    blogLayout: 'default',
    params: {
        style: 'professional',
        wordCount: 'standard',
        depth: 'deep'
    }
};

function formatHotValue(value) {
    if (value >= 10000) return (value / 10000).toFixed(1) + '万';
    return value.toString();
}

function getCategoryName(category) {
    const names = { tech: '科技', life: '生活', entertainment: '娱乐', career: '职场' };
    return names[category] || category;
}

function getCategoryColor(category) {
    const colors = {
        tech: 'bg-blue-100 text-blue-700',
        life: 'bg-green-100 text-green-700',
        entertainment: 'bg-purple-100 text-purple-700',
        career: 'bg-orange-100 text-orange-700'
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');
    toastIcon.className = type === 'success'
        ? 'fa fa-check-circle text-green-400'
        : 'fa fa-exclamation-circle text-red-400';
    toastMessage.textContent = message;
    toast.classList.remove('translate-y-20', 'opacity-0');
    setTimeout(() => toast.classList.add('translate-y-20', 'opacity-0'), 3000);
}

function showLoading(title = '正在生成...', desc = '请稍候，AI 正在努力创作中') {
    document.getElementById('loadingTitle').textContent = title;
    document.getElementById('loadingDesc').textContent = desc;
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

async function apiGet(path) {
    const resp = await fetch(API_BASE + path);
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: '请求失败' }));
        throw new Error(err.error || `HTTP ${resp.status}`);
    }
    return resp.json();
}

async function apiPost(path, body) {
    const resp = await fetch(API_BASE + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: '请求失败' }));
        throw new Error(err.error || `HTTP ${resp.status}`);
    }
    return resp.json();
}

async function apiUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    const resp = await fetch(API_BASE + '/images/upload', { method: 'POST', body: formData });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: '上传失败' }));
        throw new Error(err.error || `HTTP ${resp.status}`);
    }
    return resp.json();
}

async function fetchHotspots() {
    try {
        let url = `/hotspots?type=${state.currentCategory}&page=1&pageSize=20`;
        if (state.searchQuery) url += `&search=${encodeURIComponent(state.searchQuery)}`;
        const data = await apiGet(url);
        state.topics = data.items || [];
        renderTopics();
    } catch (e) {
        console.error('获取热点失败:', e);
        showToast('获取热点失败: ' + e.message, 'error');
        document.getElementById('topicsList').innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fa fa-exclamation-triangle text-3xl mb-3 text-yellow-500"></i>
                <p>热点加载失败</p>
                <button onclick="fetchHotspots()" class="mt-3 text-blue-600 hover:text-blue-700 text-sm">
                    <i class="fa fa-refresh mr-1"></i>重试
                </button>
            </div>`;
    }
}

function renderTopics() {
    const container = document.getElementById('topicsList');
    const topics = state.topics;

    if (!topics || topics.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fa fa-search text-3xl mb-3 text-gray-400"></i>
                <p>暂无相关热点</p>
            </div>`;
        return;
    }

    container.innerHTML = topics.map(topic => {
        const isSelected = state.selectedTopics.some(t => t.id === topic.id);
        return `<div class="topic-card border border-gray-200 rounded-xl p-4 cursor-pointer ${isSelected ? 'selected' : ''}"
                    data-id="${topic.id}">
            <div class="flex items-start justify-between gap-3 mb-2">
                <h4 class="font-semibold text-gray-800 flex-1">${topic.title}</h4>
                <span class="px-2 py-0.5 rounded-full text-xs whitespace-nowrap ${getCategoryColor(topic.type)}">${getCategoryName(topic.type)}</span>
            </div>
            <p class="text-sm text-gray-600 mb-3 line-clamp-2">${topic.content}</p>
            <div class="flex items-center justify-between text-xs text-gray-500">
                <div class="flex items-center gap-3">
                    <span class="flex items-center gap-1"><i class="fa fa-fire text-orange-500"></i>${formatHotValue(topic.hotValue)}</span>
                    <span class="flex items-center gap-1"><i class="fa fa-clock-o"></i>${topic.time}</span>
                </div>
                ${isSelected ? '<span class="text-blue-600 font-medium"><i class="fa fa-check-circle mr-1"></i>已选择</span>' : ''}
            </div>
        </div>`;
    }).join('');

    container.querySelectorAll('.topic-card').forEach(card => {
        card.addEventListener('click', () => toggleTopic(card.dataset.id));
    });
}

function updateSelectedCount() {
    document.getElementById('selectedCount').textContent = `已选择 ${state.selectedTopics.length} 个`;
}

function toggleTopic(id) {
    const topic = state.topics.find(t => t.id === id);
    if (!topic) return;
    const idx = state.selectedTopics.findIndex(t => t.id === id);
    if (idx > -1) {
        state.selectedTopics.splice(idx, 1);
    } else {
        state.selectedTopics.push(topic);
    }
    renderTopics();
    updateSelectedCount();
}

function selectAllTopics() {
    state.topics.forEach(topic => {
        if (!state.selectedTopics.some(t => t.id === topic.id)) {
            state.selectedTopics.push(topic);
        }
    });
    renderTopics();
    updateSelectedCount();
}

function clearSelection() {
    state.selectedTopics = [];
    renderTopics();
    updateSelectedCount();
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('tab-active', 'text-gray-500');
        if (btn.dataset.tab === tabName) btn.classList.add('tab-active');
        else btn.classList.add('text-gray-500');
    });
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById(`${tabName}Tab`).classList.remove('hidden');
    if (tabName === 'preview') updatePreview();
}

async function generateBlogContent() {
    if (state.selectedTopics.length === 0) {
        showToast('请先选择至少一个热点话题', 'error');
        return;
    }
    showLoading('正在生成博客...', 'AI 正在基于选中的热点创作内容');
    try {
        const resp = await apiPost('/blog/generate', {
            topics: state.selectedTopics,
            style: state.params.style,
            wordCount: state.params.wordCount,
            depth: state.params.depth
        });
        state.blogContent = resp.data;
        updateEditorFromContent();
        hideLoading();
        showToast('博客内容生成成功！');
        switchTab('preview');
    } catch (e) {
        hideLoading();
        showToast('生成失败: ' + e.message, 'error');
    }
}

function updateEditorFromContent() {
    const bc = state.blogContent;
    if (!bc) return;
    const parts = [
        bc.title,
        '',
        bc.subtitle,
        '',
        bc.introduction,
        ...bc.sections.map(s => `## ${s.heading}\n\n${s.content}`),
        '## 结语',
        '',
        bc.conclusion
    ];
    document.getElementById('blogEditor').value = parts.join('\n');
}

function updatePreview() {
    const container = document.getElementById('blogPreview');
    if (!state.blogContent) {
        container.innerHTML = `
            <div class="text-center text-gray-400 py-12">
                <i class="fa fa-file-text-o text-4xl mb-3"></i>
                <p>生成博客后可在此预览效果</p>
            </div>`;
        return;
    }
    const bc = state.blogContent;
    const imgAlign = state.imageAlign || 'center';
    const layoutClass = 'layout-' + (state.blogLayout || 'default');

    let imgHtml = '';
    if (state.images.length > 0) {
        imgHtml = state.images.map(img =>
            `<img src="${img.url || img}" alt="配图" class="align-${imgAlign}">`
        ).join('');
    }

    container.innerHTML = `
        <div class="blog-content ${layoutClass}">
            <h1>${bc.title}</h1>
            <p class="blog-subtitle">${bc.subtitle}</p>
            ${imgHtml}
            <p class="blog-intro">${bc.introduction}</p>
            ${bc.sections.map(s => `<h2>${s.heading}</h2><p>${s.content}</p>`).join('')}
            <h2>结语</h2>
            <p>${bc.conclusion}</p>
        </div>`;
}

async function generateImages() {
    const count = parseInt(document.getElementById('imageCountSelect').value);
    const style = document.getElementById('imageStyleSelect').value;
    const ratio = document.getElementById('imageRatioSelect').value;
    const desc = document.getElementById('imageDescInput').value.trim();

    const [rw, rh] = ratio.split(':').map(Number);
    const base = 400;
    let width = base * (rw / rh > 1 ? 2 : 1);
    let height = base * (rh / rw > 1 ? 2 : 1);
    if (rw === rh) { width = 600; height = 600; }

    const keyword = desc || (state.selectedTopics.length > 0
        ? state.selectedTopics.map(t => t.title).join(' ').slice(0, 30)
        : 'blog illustration');

    showLoading('正在生成图片...', `AI 正在创作 ${style} 风格图片`);
    try {
        const resp = await apiPost('/images/generate', {
            keyword, style, count: Math.min(count, 8), width, height
        });
        const newImages = resp.data || [];
        state.images = [...state.images, ...newImages];
        renderImages();
        hideLoading();
        showToast(`成功生成 ${newImages.length} 张${style}风格图片！`);
    } catch (e) {
        hideLoading();
        showToast('图片生成失败: ' + e.message, 'error');
    }
}

function renderImages() {
    const container = document.getElementById('imagesList');
    if (state.images.length === 0) {
        container.innerHTML = `<div class="text-center text-gray-400 py-8 col-span-full"><p>暂无图片</p></div>`;
        return;
    }
    container.innerHTML = state.images.map((img, idx) => `
        <div class="relative group">
            <img src="${img.url || img.placeholder || img}" alt="图片 ${idx + 1}" class="w-full h-32 object-cover rounded-xl">
            <button class="absolute top-2 right-2 w-8 h-8 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                    onclick="removeImage(${idx})"><i class="fa fa-times"></i></button>
        </div>
    `).join('');
}

function removeImage(index) {
    state.images.splice(index, 1);
    renderImages();
    showToast('图片已删除');
}

async function handleFileUpload(files) {
    if (!files || files.length === 0) return;
    for (const file of Array.from(files)) {
        if (!file.type.startsWith('image/')) {
            showToast(`${file.name} 不是图片文件`, 'error');
            continue;
        }
        try {
            const resp = await apiUpload(file);
            if (resp.success && resp.data) {
                state.images.push({ url: resp.data.url, name: resp.data.originalName });
                renderImages();
                showToast(`${file.name} 上传成功！`);
            }
        } catch (e) {
            showToast(`上传失败: ${e.message}`, 'error');
        }
    }
}

function copyContent() {
    const content = document.getElementById('blogEditor').value;
    if (!content) { showToast('没有可复制的内容', 'error'); return; }
    navigator.clipboard.writeText(content).then(
        () => showToast('内容已复制到剪贴板！'),
        () => showToast('复制失败，请手动复制', 'error')
    );
}

function exportContent(format) {
    const content = document.getElementById('blogEditor').value;
    if (!content) { showToast('没有可导出的内容', 'error'); return; }

    let filename = 'blog';
    let blobContent = content;
    let mimeType = 'text/plain';

    if (format === 'html') {
        filename += '.html';
        mimeType = 'text/html';
        const previewContent = document.getElementById('blogPreview').querySelector('.blog-content');
        blobContent = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${state.blogContent?.title || '博客'}</title><style>body{font-family:system-ui,-apple-system,sans-serif;max-width:800px;margin:0 auto;padding:40px 20px;line-height:1.8}h1{font-size:2rem}h2{font-size:1.5rem;margin-top:2rem}img{max-width:100%;border-radius:0.75rem;margin:1rem 0}</style></head><body>${previewContent?.innerHTML || content.replace(/\n/g, '<br>')}</body></html>`;
    } else if (format === 'markdown') {
        filename += '.md';
        mimeType = 'text/markdown';
    } else {
        filename += '.txt';
    }

    const blob = new Blob([blobContent], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`已导出为 ${format.toUpperCase()} 格式！`);
    document.getElementById('exportDropdown').classList.add('hidden');
}

function resetAll() {
    state.selectedTopics = [];
    state.blogContent = null;
    state.images = [];
    document.getElementById('blogEditor').value = '';
    renderTopics();
    renderImages();
    updateSelectedCount();
    updatePreview();
    showToast('已重置');
}

async function refreshTopics() {
    showLoading('正在刷新...', '正在获取最新热点');
    try {
        await apiPost('/hotspots/refresh');
        await fetchHotspots();
        hideLoading();
        showToast('热点已刷新！');
    } catch (e) {
        hideLoading();
        await fetchHotspots();
        showToast('热点已刷新（使用本地缓存）', 'success');
    }
}

function init() {
    fetchHotspots();

    document.getElementById('searchInput').addEventListener('input', (e) => {
        state.searchQuery = e.target.value;
        fetchHotspots();
    });

    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.category-btn').forEach(b => {
                b.classList.remove('bg-blue-500', 'text-white');
                b.classList.add('bg-gray-100', 'text-gray-700');
            });
            btn.classList.remove('bg-gray-100', 'text-gray-700');
            btn.classList.add('bg-blue-500', 'text-white');
            state.currentCategory = btn.dataset.category;
            fetchHotspots();
        });
    });

    document.getElementById('selectAllBtn').addEventListener('click', selectAllTopics);
    document.getElementById('clearSelectionBtn').addEventListener('click', clearSelection);
    document.getElementById('refreshBtn').addEventListener('click', refreshTopics);

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    document.getElementById('styleSelect').addEventListener('change', e => { state.params.style = e.target.value; });
    document.getElementById('wordCountSelect').addEventListener('change', e => { state.params.wordCount = e.target.value; });
    document.getElementById('depthSelect').addEventListener('change', e => { state.params.depth = e.target.value; });

    document.getElementById('generateContentBtn').addEventListener('click', generateBlogContent);
    document.getElementById('generateImagesBtn').addEventListener('click', generateImages);

    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', e => handleFileUpload(e.target.files));
    uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('drag-over'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('drag-over'));
    uploadArea.addEventListener('drop', e => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        handleFileUpload(e.dataTransfer.files);
    });

    document.getElementById('copyBtn').addEventListener('click', copyContent);
    document.getElementById('resetBtn').addEventListener('click', resetAll);

    const exportBtn = document.getElementById('exportBtn');
    const exportDropdown = document.getElementById('exportDropdown');
    exportBtn.addEventListener('click', () => exportDropdown.classList.toggle('hidden'));
    document.querySelectorAll('.export-option').forEach(opt => {
        opt.addEventListener('click', () => exportContent(opt.dataset.format));
    });
    document.addEventListener('click', e => {
        if (!exportBtn.contains(e.target) && !exportDropdown.contains(e.target)) {
            exportDropdown.classList.add('hidden');
        }
    });

    document.getElementById('helpBtn').addEventListener('click', () => {
        showToast('使用说明：选择热点 → 设置参数 → 生成内容 → 添加图片 → 导出');
    });

    document.querySelectorAll('.align-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.align-btn').forEach(b => {
                b.classList.remove('bg-blue-100', 'text-blue-700');
                b.classList.add('bg-gray-100', 'text-gray-600');
            });
            btn.classList.remove('bg-gray-100', 'text-gray-600');
            btn.classList.add('bg-blue-100', 'text-blue-700');
            state.imageAlign = btn.dataset.align;
            updatePreview();
        });
    });

    document.querySelectorAll('.layout-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.layout-btn').forEach(b => {
                b.classList.remove('bg-blue-100', 'text-blue-700');
                b.classList.add('bg-gray-100', 'text-gray-600');
            });
            btn.classList.remove('bg-gray-100', 'text-gray-600');
            btn.classList.add('bg-blue-100', 'text-blue-700');
            state.blogLayout = btn.dataset.layout;
            updatePreview();
        });
    });

    // ——— API 设置面板 ———
    const settingsOverlay = document.getElementById('settingsOverlay');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');

    document.getElementById('settingsBtn').addEventListener('click', openSettings);
    closeSettingsBtn.addEventListener('click', () => { settingsOverlay.classList.add('hidden'); });
    settingsOverlay.addEventListener('click', (e) => {
        if (e.target === settingsOverlay) settingsOverlay.classList.add('hidden');
    });

    document.getElementById('saveAiConfigBtn').addEventListener('click', saveAiConfig);
    document.getElementById('saveImageConfigBtn').addEventListener('click', saveImageConfig);

    loadConfig();

    document.getElementById('imageDescInput').addEventListener('input', () => {
        const desc = document.getElementById('imageDescInput').value.trim();
        document.getElementById('generateImagesBtn').innerHTML = desc
            ? '<i class="fa fa-paint-brush"></i> 生成 "' + desc.slice(0, 12) + (desc.length > 12 ? '...' : '') + '" 图片'
            : '<i class="fa fa-paint-brush"></i> 生成 AI 图片';
    });
}

async function openSettings() {
    document.getElementById('settingsOverlay').classList.remove('hidden');
    await loadConfig();
}

async function loadConfig() {
    try {
        const resp = await apiGet('/config');
        // 文本 AI
        if (resp.ai) {
            document.getElementById('aiBaseUrl').value = resp.ai.base_url || 'https://api.openai.com/v1';
            document.getElementById('aiModel').value = resp.ai.model || 'gpt-3.5-turbo';
            const aiStatus = document.getElementById('aiStatus');
            const aiKeyHint = document.getElementById('aiKeyHint');
            if (resp.ai.api_key_set) {
                aiStatus.className = 'ml-auto px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700';
                aiStatus.textContent = '已配置';
                aiKeyHint.textContent = '已配置: ' + (resp.ai.api_key || '****');
                aiKeyHint.classList.remove('hidden');
                document.getElementById('aiApiKey').placeholder = '已配置（留空不修改）';
            } else {
                aiStatus.className = 'ml-auto px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-500';
                aiStatus.textContent = '未配置';
                aiKeyHint.classList.add('hidden');
                document.getElementById('aiApiKey').placeholder = 'sk-xxxxxxxxxxxxxxxx';
            }
        }
        // 图片 AI
        if (resp.image) {
            document.getElementById('imageBaseUrl').value = resp.image.base_url || 'https://api.openai.com/v1';
            document.getElementById('imageModel').value = resp.image.model || 'dall-e-3';
            const imgStatus = document.getElementById('imageStatus');
            const imgKeyHint = document.getElementById('imageKeyHint');
            if (resp.image.api_key_set) {
                imgStatus.className = 'ml-auto px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700';
                imgStatus.textContent = '已配置';
                imgKeyHint.textContent = '已配置: ' + (resp.image.api_key || '****');
                imgKeyHint.classList.remove('hidden');
                document.getElementById('imageApiKey').placeholder = '已配置（留空不修改）';
            } else {
                imgStatus.className = 'ml-auto px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-500';
                imgStatus.textContent = '未配置';
                imgKeyHint.classList.add('hidden');
                document.getElementById('imageApiKey').placeholder = 'sk-xxxxxxxxxxxxxxxx';
            }
        }
    } catch (e) {
        console.error('加载配置失败:', e);
    }
}

async function saveAiConfig() {
    const data = {
        base_url: document.getElementById('aiBaseUrl').value.trim(),
        model: document.getElementById('aiModel').value.trim()
    };
    const key = document.getElementById('aiApiKey').value.trim();
    if (key) data.api_key = key;

    if (!data.base_url || !data.model) {
        showToast('API 地址和模型名称不能为空', 'error');
        return;
    }

    try {
        await apiPut('/config/ai', data);
        showToast('AI 文本生成配置已保存！');
        await loadConfig();
    } catch (e) {
        showToast('保存失败: ' + e.message, 'error');
    }
}

async function saveImageConfig() {
    const data = {
        base_url: document.getElementById('imageBaseUrl').value.trim(),
        model: document.getElementById('imageModel').value.trim()
    };
    const key = document.getElementById('imageApiKey').value.trim();
    if (key) data.api_key = key;

    if (!data.base_url || !data.model) {
        showToast('API 地址和模型名称不能为空', 'error');
        return;
    }

    try {
        await apiPut('/config/image', data);
        showToast('AI 图片生成配置已保存！');
        await loadConfig();
    } catch (e) {
        showToast('保存失败: ' + e.message, 'error');
    }
}

async function apiPut(path, body) {
    const resp = await fetch(API_BASE + path, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: '请求失败' }));
        throw new Error(err.error || `HTTP ${resp.status}`);
    }
    return resp.json();
}

document.addEventListener('DOMContentLoaded', init);
