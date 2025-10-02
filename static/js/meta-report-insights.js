// Meta Report Insights Functions
let metaReportData = null;

function initializeMetaReportInsights() {
    console.log('Initializing Meta Report Insights...');
    
    // Load initial data
    loadMetaReportData();
    
    // Event listeners
    const refreshBtn = document.getElementById('btn-refresh-meta-report');
    const exportBtn = document.getElementById('btn-export-meta-report');
    const datePreset = document.getElementById('meta-report-date-preset');
    const aiBtn = document.getElementById('btn-meta-content-ai');
    
    console.log('Meta Report elements found:', {
        refreshBtn: !!refreshBtn,
        exportBtn: !!exportBtn,
        datePreset: !!datePreset
    });
    
    if (refreshBtn) refreshBtn.addEventListener('click', loadMetaReportData);
    if (exportBtn) exportBtn.addEventListener('click', exportMetaReportData);
    if (datePreset) datePreset.addEventListener('change', loadMetaReportData);
    if (aiBtn) aiBtn.addEventListener('click', loadMetaContentInsights);
    // Auto-run content insights if button exists
    if (aiBtn) loadMetaContentInsights();
}

// Global filter integration
function updateMetaReportWithFilters(filterParams) {
    console.log('Updating Meta Report with filters:', filterParams);
    loadMetaReportData(filterParams);
}

async function loadMetaReportData(customParams = null) {
    try {
        console.log('Loading Meta Report data...');
        let preset = 'last_30d';
        let url = '/api/meta-report-insights';
        
        if (customParams) {
            // Use global filter parameters
            const params = new URLSearchParams();
            if (customParams.date_preset) params.append('date_preset', customParams.date_preset);
            if (customParams.since) params.append('since', customParams.since);
            if (customParams.until) params.append('until', customParams.until);
            if (customParams.campaign_id) params.append('campaign_id', customParams.campaign_id);
            if (customParams.brand) params.append('brand', customParams.brand);
            
            url += '?' + params.toString();
            preset = customParams.date_preset || 'last_30d';
        } else {
            // Use local filter
            preset = document.getElementById('meta-report-date-preset').value;
            url += `?date_preset=${encodeURIComponent(preset)}`;
        }
        
        const tbody = document.getElementById('meta-report-table');
        
        console.log('Preset:', preset, 'Table body found:', !!tbody);
        
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="14" class="px-6 py-4 text-center text-gray-500">Đang tải dữ liệu...</td></tr>';
        }
        
        const response = await fetch(url);
        console.log('API response status:', response.status);
        
        const data = await response.json();
        console.log('API response data:', data);
        
        if (data.error) {
            console.error('Meta Report Insights error:', data.error);
            let errorMessage = data.error;
            if (typeof data.error === 'object' && data.error.message) {
                errorMessage = data.error.message;
            }
            
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="14" class="px-6 py-4 text-center text-red-500">Lỗi: ${errorMessage}</td></tr>`;
            }
            return;
        }
        
        metaReportData = data;
        updateMetaReportTable(data);
        updateMetaReportSummaryCards(data);
        updateBrandAnalysis(data);
        updateContentAnalysis(data);
        createMetaReportCharts(data);
        
    } catch (error) {
        console.error('Error loading meta report data:', error);
        const tbody = document.getElementById('meta-report-table');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="14" class="px-6 py-4 text-center text-red-500">Lỗi kết nối khi tải dữ liệu</td></tr>';
        }
    }
}

async function loadMetaContentInsights(){
    try{
        const target = document.getElementById('meta-ai-content');
        const s = document.getElementById('meta-ai-since')?.value?.trim();
        const u = document.getElementById('meta-ai-until')?.value?.trim();
        if(target) target.textContent = 'Đang lấy bài viết và phân tích AI...';
        const qs = new URLSearchParams({ limit: '50' });
        if(s) qs.set('since', s);
        if(u) qs.set('until', u);
        const res = await fetch(`/api/meta-report-content-insights?${qs.toString()}`);
        const data = await res.json();
        if(data.error){
            target.textContent = `Lỗi: ${typeof data.error==='object'?JSON.stringify(data.error):data.error}`;
            return;
        }
        const raw = data.ai?.insights || 'Không có kết quả AI';
        const cleaned = sanitizeAIText(raw);
        target.innerHTML = renderAITextAsHtml(cleaned);
        renderMetaPostsCards(data.posts||[]);
    }catch(err){
        const target = document.getElementById('meta-ai-content');
        if(target) target.textContent = `Lỗi kết nối: ${err}`;
    }
}

function sanitizeAIText(text){
    if(!text) return '';
    // Remove markdown artifacts like repeated # and leading * spaces
    let t = text.replace(/[\t\r]+/g,'\n');
    // Normalize bullets: lines starting with * or - (remove asterisks)
    t = t.replace(/^\s*\*+\s+/gm, '• ');
    t = t.replace(/^\s*\-+\s+/gm, '• ');
    // Remove excessive ### while keeping heading markers for rendering
    t = t.replace(/\n{3,}/g, '\n\n');
    return t.trim();
}

// Agency report rendering
async function loadAgencyReport() {
    try {
        const wrap = document.getElementById('agency-funnel');
        if (!wrap) return;
        wrap.textContent = 'Đang tải phễu...';
        const res = await fetch('/api/agency-report');
        const data = await res.json();
        if (!res.ok || data.error) {
            wrap.textContent = 'Không thể tải dữ liệu phễu';
            return;
        }
        // cache spend and revenue for annotations
        window.metaAgencyCacheSpend = Number(data.spend || 0);
        window.metaAgencyPurchaseValue = Number(data.purchase_value || 0);
        // Render SVG funnel chart with gradients, shadows and side annotations
        const funnel = (data.funnel || []).slice(0, 6);
        const max = Math.max(1, ...funnel.map(f => f.total || 0));
        const colors = ['#0ea5e9','#0bb49f','#f59e0b','#f97316','#ef4444','#8b5cf6'];
        const rect = wrap.getBoundingClientRect();
        const available = (rect.width || 680);
        // Use almost full width for the SVG; annotations live inside SVG now
        const W = Math.max(520, Math.floor(available - 40));
        const H = Math.max(280, 90 * funnel.length + 20);
        const topWidth = Math.floor(W * 0.86);
        const minWidth = Math.floor(W * 0.42);
        const stageHeight = Math.floor((H - 40) / funnel.length) - 6;
        const topX = (W - topWidth) / 2;

        // desired widths proportional to totals; enforce decreasing shape
        const target = funnel.map(s => Math.max(minWidth, (s.total / max) * topWidth));
        const widths = [];
        for (let i = 0; i < target.length; i++) {
            const prev = i === 0 ? topWidth : widths[i-1] - 10;
            widths.push(Math.max(minWidth, Math.min(prev, target[i])));
        }

        // defs: gradients and soft shadow
        const defs = () => {
            let g = '<defs>';
            g += `
            <filter id="funnelShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.15"/>
            </filter>`;
            for (let i = 0; i < funnel.length; i++) {
                const c = colors[i%colors.length];
                g += `
                <linearGradient id="grad${i}" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="${c}" stop-opacity="0.95"/>
                    <stop offset="100%" stop-color="${c}" stop-opacity="0.75"/>
                </linearGradient>`;
            }
            g += '</defs>';
            return g;
        };

        let y = 20;
        let svg = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
        svg += defs();
        // background subtle grid
        svg += `<rect x="0" y="0" width="${W}" height="${H}" fill="#ffffff"/>`;
        for (let i = 0; i < funnel.length; i++) {
            const wTop = i === 0 ? topWidth : widths[i-1];
            const wBot = widths[i];
            const xTop = (W - wTop) / 2;
            const xBot = (W - wBot) / 2;
            const h = stageHeight;
            const path = `M ${xTop} ${y} L ${xTop + wTop} ${y} L ${xBot + wBot} ${y + h} L ${xBot} ${y + h} Z`;
            svg += `<path d="${path}" fill="url(#grad${i})" stroke="#ffffff" stroke-width="2" filter="url(#funnelShadow)"/>`;
            // labels
            const label = funnel[i].title || '';
            const value = (funnel[i].total || 0).toLocaleString('vi-VN');
            svg += `<text x="${W/2}" y="${y + h/2 - 4}" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="600">${label}</text>`;
            svg += `<text x="${W/2}" y="${y + h/2 + 14}" text-anchor="middle" fill="#ffffff" font-size="16" font-weight="700">${value}</text>`;
            // right side annotation with cost ratios (skip for first stage - impressions)
            if (i > 0) {
                const leftVal = funnel[i-1]?.total || funnel[i].total || 0;
                const rightVal = funnel[i].total || 0;
                const ratio = leftVal > 0 ? leftVal / rightVal : 0; // proxy if spend not available per stage
                // mapping labels for remaining stages from top to bottom
                const rightLabels = ['Tương tác','Quan tâm','Tiếp cận', 'Chuyển đổi','Doanh thu'];
                const labelRight = rightLabels[Math.min(i-1, rightLabels.length-1)] || '';
                const displayVal = (()=>{
                    if(i===funnel.length-1){
                        // Last stage: revenue value
                        return (window.metaAgencyPurchaseValue||0).toLocaleString('vi-VN');
                    }
                    return ratio>0? ratio.toFixed(2): '0.00';
                })();
                const annX = Math.min(W - 20 - 240, xTop + wTop + 24);
                const annY = y + h/2 - 14;
                const boxW = 240;
                svg += `<line x1="${xTop + wTop - 4}" y1="${y + h/2}" x2="${annX - 8}" y2="${annY + 14}" stroke="#cbd5e1" stroke-width="1.5"/>`;
                svg += `<rect x="${annX}" y="${annY}" rx="8" ry="8" width="${boxW}" height="28" fill="#ffffff" stroke="#e2e8f0"/>`;
                svg += `<text x="${annX + 10}" y="${annY + 19}" fill="#334155" font-size="12">${labelRight}</text>`;
                svg += `<text x="${annX + boxW - 10}" y="${annY + 19}" text-anchor="end" fill="#0f172a" font-size="12" font-weight="700">${displayVal}</text>`;
            }
            y += h + 12;
        }
        svg += '</svg>';
        wrap.innerHTML = svg;

        // Fill metric groups
        const groups = data.groups || {};
        const g = (key, id, fmtPct=false) => {
            const item = (groups[key]||[]).find(x=>x.key===id);
            return item || { total: 0, delta_pct: 0 };
        };
        const setVal = (el, val, isPct=false) => {
            const e = document.getElementById(el);
            if (!e) return;
            e.textContent = isPct ? `${Number(val||0).toFixed(2)}%` : (typeof val==='number'? val.toLocaleString('vi-VN') : val);
        };
        const setDelta = (el, val) => {
            const e = document.getElementById(el);
            if (!e) return;
            // Remove percentage display for agency report as requested
            e.textContent = '';
            e.style.display = 'none';
        };

        const dImp = g('display','impressions');
        setVal('agency-display-impressions', dImp.total);
        setDelta('agency-display-impressions-delta', dImp.delta_pct);

        const dReach = g('display','reach');
        setVal('agency-display-reach', dReach.total);
        setDelta('agency-display-reach-delta', dReach.delta_pct);

        const dCtr = g('display','ctr');
        setVal('agency-display-ctr', dCtr.total, true);
        setDelta('agency-display-ctr-delta', dCtr.delta_pct);

        const eTotal = g('engagement','engagement');
        setVal('agency-engagement-total', eTotal.total);
        setDelta('agency-engagement-total-delta', eTotal.delta_pct);

        const eClicks = g('engagement','link_clicks');
        setVal('agency-engagement-clicks', eClicks.total);
        setDelta('agency-engagement-clicks-delta', eClicks.delta_pct);

        const cMsg = g('conversion','messaging_starts');
        setVal('agency-conv-messages', cMsg.total);
        setDelta('agency-conv-messages-delta', cMsg.delta_pct);

        const cPur = g('conversion','purchases');
        setVal('agency-conv-purchase', cPur.total);
        setDelta('agency-conv-purchase-delta', cPur.delta_pct);

        const cVal = g('conversion','purchase_value');
        setVal('agency-conv-value', cVal.total);
        setDelta('agency-conv-value-delta', cVal.delta_pct);
    } catch (e) {
        console.error('loadAgencyReport error', e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadAgencyReport();
});

function renderAITextAsHtml(text){
    // Simple renderer: convert headings and bullets, and inline bold/italic
    const lines = text.split(/\n/);
    const html = [];
    for(const line of lines){
        if(/^\s*#{1,6}\s+/.test(line)){
            const lvl = (line.match(/^\s*(#{1,6})\s+/) || [,'#'])[1].length;
            const content = line.replace(/^\s*#{1,6}\s+/, '');
            html.push(`<div class="font-semibold mt-2 mb-1" style="font-size:${Math.max(16,22-(lvl*1))}px">${formatInline(content)}</div>`);
        } else if(/^\s*•\s+/.test(line)){
            html.push(`<div class="pl-3">• ${formatInline(line.replace(/^\s*•\s+/,''))}</div>`);
        } else if(line.trim().length===0){
            html.push('<div class="h-2"></div>');
        } else {
            html.push(`<div>${formatInline(line)}</div>`);
        }
    }
    return html.join('');
}

function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
}

function formatInline(s){
    if(!s) return '';
    // Convert simple markdown bold/italic while keeping HTML safe
    let t = String(s);
    // Mark tokens to avoid escaping them
    t = t.replace(/\*\*(.+?)\*\*/g, '<<b>>$1<</b>>');
    t = t.replace(/\*(.+?)\*/g, '<<i>>$1<</i>>');
    // Escape HTML
    t = escapeHtml(t);
    // Restore tokens
    t = t.replace(/&lt;&lt;b&gt;&gt;/g, '<b>').replace(/&lt;&lt;\/b&gt;&gt;/g, '</b>');
    t = t.replace(/&lt;&lt;i&gt;&gt;/g, '<i>').replace(/&lt;&lt;\/i&gt;&gt;/g, '</i>');
    return t;
}

function renderMetaPostsCards(posts){
    const wrap = document.getElementById('meta-ai-posts');
    if(!wrap) return;
    wrap.innerHTML = '';
    const top = posts.slice(0,9).sort((a,b)=>{
        const as=(a.reactions_count||0)+(a.comments_count||0)+(a.shares_count||0);
        const bs=(b.reactions_count||0)+(b.comments_count||0)+(b.shares_count||0);
        return bs-as;
    });
    for(const p of top){
        const total = (p.reactions_count||0)+(p.comments_count||0)+(p.shares_count||0);
        const msg = (p.message||'').slice(0,160);
        const created = (p.created_time||'').replace('T',' ').split('+')[0];
        const link = p.permalink_url ? p.permalink_url : `https://facebook.com/${encodeURIComponent(p.id||'')}`;
        const card = document.createElement('a');
        card.href = link;
        card.target = '_blank';
        card.rel = 'noopener noreferrer';
        card.className = 'block meta-report-card hover:shadow-md border cursor-pointer';
        card.innerHTML = `
            <div class="text-sm text-gray-600 mb-1">${escapeHtml(created)}</div>
            <div class="font-medium text-gray-900 mb-2">${escapeHtml(msg)}</div>
            <div class="flex gap-4 text-sm">
                <div>👍 ${NUM_FMT.format(p.reactions_count||0)}</div>
                <div>💬 ${NUM_FMT.format(p.comments_count||0)}</div>
                <div>↗️ ${NUM_FMT.format(p.shares_count||0)}</div>
                <div class="ml-auto font-semibold">Tổng: ${NUM_FMT.format(total)}</div>
            </div>
        `;
        wrap.appendChild(card);
    }
}

function updateMetaReportTable(data) {
    const tbody = document.getElementById('meta-report-table');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (!data.monthly_data || data.monthly_data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="14" class="px-6 py-4 text-center text-gray-500">Không có dữ liệu</td></tr>';
        return;
    }
    
    data.monthly_data.forEach(month => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        // Calculate metrics
        const spend = parseFloat(month.spend || 0);
        const reach = parseInt(month.reach || 0);
        const impressions = parseInt(month.impressions || 0);
        const clicks = parseInt(month.clicks || 0);
        const engagement = parseInt(month.engagement || 0);
        const videoViews = parseInt(month.video_views || 0);
        const linkClicks = parseInt(month.link_clicks || 0);
        
        // Calculate derived metrics
        const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
        const cpc = clicks > 0 ? spend / clicks : 0;
        const engagementRate = impressions > 0 ? (engagement / impressions) * 100 : 0;
        
        // Format brands and content formats
        const brandsText = month.brands ? month.brands.join(', ') : 'Unknown';
        const contentFormatsText = month.content_formats ? month.content_formats.join(', ') : 'Unknown';
        
        row.innerHTML = `
            <td class="px-2 py-3 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                ${month.month}
            </td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-500">${brandsText}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-500">${contentFormatsText}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${month.campaign_count}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900 font-medium">${VND_FMT.format(spend)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(reach)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(impressions)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(clicks)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${ctr.toFixed(2)}%</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(cpc)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(engagement)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${engagementRate.toFixed(2)}%</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(videoViews)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(linkClicks)}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function updateMetaReportSummaryCards(data) {
    if (!data.monthly_data || data.monthly_data.length === 0) return;
    
    // Calculate totals
    let totalBrands = 0;
    let totalContentFormats = 0;
    let totalSpend = 0;
    let totalReach = 0;
    let totalEngagement = 0;
    let totalClicks = 0;
    let totalImpressions = 0;
    
    const allBrands = new Set();
    const allContentFormats = new Set();
    
    data.monthly_data.forEach(month => {
        totalSpend += parseFloat(month.spend || 0);
        totalReach += parseInt(month.reach || 0);
        totalEngagement += parseInt(month.engagement || 0);
        totalClicks += parseInt(month.clicks || 0);
        totalImpressions += parseInt(month.impressions || 0);
        
        if (month.brands) {
            month.brands.forEach(brand => allBrands.add(brand));
        }
        if (month.content_formats) {
            month.content_formats.forEach(format => allContentFormats.add(format));
        }
    });
    
    totalBrands = allBrands.size;
    totalContentFormats = allContentFormats.size;
    
    const avgCtr = totalImpressions > 0 ? (totalClicks / totalImpressions) * 100 : 0;
    
    // Update summary cards
    const elements = {
        'meta-total-brands': totalBrands,
        'meta-total-content-formats': totalContentFormats,
        'meta-total-spend': VND_FMT.format(totalSpend),
        'meta-total-reach': NUM_FMT.format(totalReach),
        'meta-total-engagement': NUM_FMT.format(totalEngagement),
        'meta-avg-ctr': avgCtr.toFixed(2) + '%'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    });
}

function updateBrandAnalysis(data) {
    const brandList = document.getElementById('brand-analysis-list');
    if (!brandList || !data.brand_analysis) return;
    
    brandList.innerHTML = '';
    
    Object.entries(data.brand_analysis).forEach(([brand, analysis]) => {
        const div = document.createElement('div');
        div.className = 'meta-report-analysis-item';
        
        const spend = parseFloat(analysis.total_spend || 0);
        const impressions = parseInt(analysis.total_impressions || 0);
        const clicks = parseInt(analysis.total_clicks || 0);
        const engagement = parseInt(analysis.total_engagement || 0);
        
        const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
        const engagementRate = impressions > 0 ? (engagement / impressions) * 100 : 0;
        
        div.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <div class="font-medium text-gray-900">${brand}</div>
                    <div class="text-xs text-gray-500">${analysis.campaign_count} campaigns</div>
                </div>
                <div class="text-right">
                    <div class="text-sm font-medium text-gray-900">${VND_FMT.format(spend)}</div>
                    <div class="text-xs text-gray-500">CTR: ${ctr.toFixed(2)}%</div>
                </div>
            </div>
            <div class="mt-2 text-xs text-gray-600">
                Reach: ${NUM_FMT.format(impressions)} | Engagement: ${NUM_FMT.format(engagement)} (${engagementRate.toFixed(2)}%)
            </div>
        `;
        
        brandList.appendChild(div);
    });
}

function updateContentAnalysis(data) {
    const contentList = document.getElementById('content-analysis-list');
    if (!contentList || !data.content_analysis) return;
    
    contentList.innerHTML = '';
    
    Object.entries(data.content_analysis).forEach(([format, analysis]) => {
        const div = document.createElement('div');
        div.className = 'meta-report-analysis-item';
        
        const spend = parseFloat(analysis.total_spend || 0);
        const impressions = parseInt(analysis.total_impressions || 0);
        const clicks = parseInt(analysis.total_clicks || 0);
        const engagement = parseInt(analysis.total_engagement || 0);
        const performanceScore = parseFloat(analysis.performance_score || 0);
        
        const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
        const engagementRate = impressions > 0 ? (engagement / impressions) * 100 : 0;
        
        div.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <div class="font-medium text-gray-900">${format}</div>
                    <div class="text-xs text-gray-500">${analysis.campaign_count} campaigns</div>
                </div>
                <div class="text-right">
                    <div class="text-sm font-medium text-gray-900">Score: ${performanceScore.toFixed(2)}</div>
                    <div class="text-xs text-gray-500">CTR: ${ctr.toFixed(2)}%</div>
                </div>
            </div>
            <div class="mt-2 text-xs text-gray-600">
                Spend: ${VND_FMT.format(spend)} | Engagement: ${NUM_FMT.format(engagement)} (${engagementRate.toFixed(2)}%)
            </div>
        `;
        
        contentList.appendChild(div);
    });
}

function createMetaReportCharts(data) {
    // Brand Chart
    if (data.brand_analysis) {
        const brandCtx = document.getElementById('brand-chart');
        if (brandCtx) {
            const ctx = brandCtx.getContext('2d');
            if (window.charts && window.charts.brand) {
                window.charts.brand.destroy();
            }
            
            const brandEntries = Object.entries(data.brand_analysis).slice(0, 10);
            const brandLabels = brandEntries.map(([brand]) => brand);
            const brandSpend = brandEntries.map(([, analysis]) => parseFloat(analysis.total_spend || 0));
            
            window.charts = window.charts || {};
            window.charts.brand = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: brandLabels,
                    datasets: [{
                        label: 'Chi tiêu',
                        data: brandSpend,
                        backgroundColor: '#247ba0'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }
    }
    
    // Content Format Chart
    if (data.content_analysis) {
        const contentCtx = document.getElementById('content-format-chart');
        if (contentCtx) {
            const ctx = contentCtx.getContext('2d');
            if (window.charts && window.charts.contentFormat) {
                window.charts.contentFormat.destroy();
            }
            
            const contentEntries = Object.entries(data.content_analysis).slice(0, 10);
            const contentLabels = contentEntries.map(([format]) => format);
            const contentScores = contentEntries.map(([, analysis]) => parseFloat(analysis.performance_score || 0));
            
            window.charts = window.charts || {};
            window.charts.contentFormat = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: contentLabels,
                    datasets: [{
                        data: contentScores,
                        backgroundColor: ['#247ba0', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }
    }
    
    // Monthly Trends Chart
    if (data.monthly_data && data.monthly_data.length > 0) {
        const trendsCtx = document.getElementById('monthly-trends-chart');
        if (trendsCtx) {
            const ctx = trendsCtx.getContext('2d');
            if (window.charts && window.charts.monthlyTrends) {
                window.charts.monthlyTrends.destroy();
            }
            
            const months = data.monthly_data.map(month => month.month);
            const spendData = data.monthly_data.map(month => parseFloat(month.spend || 0));
            const reachData = data.monthly_data.map(month => parseInt(month.reach || 0));
            const engagementData = data.monthly_data.map(month => parseInt(month.engagement || 0));
            
            window.charts = window.charts || {};
            window.charts.monthlyTrends = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: months,
                    datasets: [
                        {
                            label: 'Chi tiêu',
                            data: spendData,
                            borderColor: '#247ba0',
                            backgroundColor: 'rgba(36,123,160,0.1)',
                            tension: 0.3,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Reach',
                            data: reachData,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16,185,129,0.1)',
                            tension: 0.3,
                            yAxisID: 'y1'
                        },
                        {
                            label: 'Engagement',
                            data: engagementData,
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245,158,11,0.1)',
                            tension: 0.3,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { type: 'linear', display: true, position: 'left' },
                        y1: { type: 'linear', display: true, position: 'right', grid: { drawOnChartArea: false } }
                    }
                }
            });
        }
    }
}

function exportMetaReportData() {
    if (!metaReportData || !metaReportData.monthly_data) {
        alert('Không có dữ liệu để export');
        return;
    }
    
    const rows = metaReportData.monthly_data.map(month => {
        const spend = parseFloat(month.spend || 0);
        const reach = parseInt(month.reach || 0);
        const impressions = parseInt(month.impressions || 0);
        const clicks = parseInt(month.clicks || 0);
        const engagement = parseInt(month.engagement || 0);
        const videoViews = parseInt(month.video_views || 0);
        const linkClicks = parseInt(month.link_clicks || 0);
        
        const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
        const cpc = clicks > 0 ? spend / clicks : 0;
        const engagementRate = impressions > 0 ? (engagement / impressions) * 100 : 0;
        
        return {
            'Tháng': month.month,
            'Thương hiệu': month.brands ? month.brands.join(', ') : 'Unknown',
            'Định dạng nội dung': month.content_formats ? month.content_formats.join(', ') : 'Unknown',
            'Chiến dịch': month.campaign_count,
            'Chi tiêu': spend,
            'Reach': reach,
            'Impressions': impressions,
            'Clicks': clicks,
            'CTR': ctr,
            'CPC': cpc,
            'Engagement': engagement,
            'Engagement Rate': engagementRate,
            'Video Views': videoViews,
            'Link Clicks': linkClicks
        };
    });
    
    const csv = toCSV(rows);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `meta-report-insights-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}
