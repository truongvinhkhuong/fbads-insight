// JavaScript for Campaign Insights functionality

async function viewInsights(campaignId, status) {
    try {
        // Align insights with current date range selection
        const preset = document.getElementById('date-preset')?.value || 'last_30d';
        let q = `date_preset=${encodeURIComponent(preset)}`;
        if (preset === 'custom') {
            const s = document.getElementById('since').value;
            const u = document.getElementById('until').value;
            if (s && u) q = `since=${encodeURIComponent(s)}&until=${encodeURIComponent(u)}`;
        }
        const res = await fetch(`/api/campaign-insights?campaign_id=${encodeURIComponent(campaignId)}&status=${encodeURIComponent(status||'')}&${q}`);
        const data = await res.json();
        if (data.error) {
            console.warn('Insights error', data.error);
            const note = document.getElementById('insights-note');
            if (note) {
                let errorMessage = data.error;
                if (typeof data.error === 'object' && data.error.message) {
                    errorMessage = data.error.message;
                }
                
                // Check for token expiration
                if (errorMessage.includes('expired') || errorMessage.includes('Session has expired')) {
                    errorMessage = 'Token Facebook đã hết hạn. Vui lòng cập nhật token mới trong file .env';
                } else if (errorMessage.includes('190')) {
                    errorMessage = 'Token Facebook không hợp lệ hoặc đã hết hạn. Vui lòng cập nhật token mới.';
                }
                
                note.textContent = errorMessage;
                note.classList.remove('hidden');
            }
            return;
        }
        const panel = document.getElementById('insights-panel');
        panel.classList.remove('hidden'); 
        panel.style.display='block';
        const vndFmt = new Intl.NumberFormat('vi-VN',{style:'currency',currency:'VND',maximumFractionDigits:0});
        document.getElementById('insights-imp').textContent = (data.totals.impressions||0).toLocaleString('vi-VN');
        document.getElementById('insights-clicks').textContent = (data.totals.clicks||0).toLocaleString('vi-VN');
        document.getElementById('insights-spend').textContent = vndFmt.format(parseFloat(data.totals.spend||0));
        const rows = Array.isArray(data.daily)?data.daily:[];
        const labels = rows.map(d=>d.date_start||d.date||d.date_stop||'').slice(-30);
        const imp = rows.map(d=>parseInt(d.impressions||0)).slice(-30);
        const spend = rows.map(d=>parseFloat(d.spend||0)).slice(-30);
        const ctx = document.getElementById('insightsChart').getContext('2d');
        charts.insights && charts.insights.destroy();
        charts.insights = new Chart(ctx,{
            type:'line',
            data:{
                labels,
                datasets:[{
                    label:'Impressions',
                    data:imp,
                    borderColor:'#247ba0',
                    backgroundColor:'rgba(36,123,160,0.15)',
                    tension:.3,
                    fill:true
                },{
                    label:'Spend',
                    data:spend,
                    borderColor:'#ef4444',
                    backgroundColor:'rgba(239,68,68,0.1)',
                    tension:.3,
                    yAxisID:'y1'
                }]
            },
            options:{
                responsive:true,
                maintainAspectRatio:false,
                scales:{
                    y:{beginAtZero:true},
                    y1:{position:'right',beginAtZero:true}
                }
            }
        });
        console.log('INSIGHTS', {labels, rows});
        // Hiển thị thêm các số liệu tổng hợp
        document.getElementById('insights-reach').textContent = (data.totals.reach||0).toLocaleString('vi-VN');
        document.getElementById('insights-ctr').textContent = ((data.totals.ctr||0).toFixed(2))+'%';
        document.getElementById('insights-frequency').textContent = (data.totals.frequency||0).toFixed(2);
        document.getElementById('insights-link-clicks').textContent = (data.totals.inline_link_clicks||0).toLocaleString('vi-VN');
        document.getElementById('insights-unique-link-clicks').textContent = (data.totals.unique_inline_link_clicks||0).toLocaleString('vi-VN');
        document.getElementById('insights-engagement').textContent = (data.totals.post_engagement||0).toLocaleString('vi-VN');
        document.getElementById('insights-photo-views').textContent = (data.totals.photo_view||0).toLocaleString('vi-VN');
        document.getElementById('insights-video-views').textContent = (data.totals.video_views||0).toLocaleString('vi-VN');
        const totalViews = (data.totals.impressions||0) + (data.totals.video_views||0);
        document.getElementById('insights-total-views').textContent = totalViews.toLocaleString('vi-VN');

        // Render funnel chart
        renderFunnelChart(data.totals);

        // Show fallback note if any
        const note = document.getElementById('insights-note');
        if (note) {
            if (data.note) { 
                note.textContent = data.note; 
                note.classList.remove('hidden'); 
            }
            else { 
                note.textContent=''; 
                note.classList.add('hidden'); 
            }
        }

        panel.scrollIntoView({behavior:'smooth',block:'start'});
    } catch (e) { 
        console.error(e); 
    }
}

// Funnel Chart Function - 3D Style
function renderFunnelChart(totals) {
    // Clear any existing chart
    charts.funnel && charts.funnel.destroy();
    
    // Calculate funnel metrics
    const impressions = parseInt(totals.impressions || 0);
    const clicks = parseInt(totals.clicks || 0);
    const linkClicks = parseInt(totals.inline_link_clicks || 0);
    const engagement = parseInt(totals.post_engagement || 0);
    const reach = parseInt(totals.reach || 0);
    const msgStarts = parseInt(totals.messaging_starts || 0);
    const purchases = parseInt(totals.purchases || 0);
    const spend = parseFloat(totals.spend || 0);
    
    // Calculate cost metrics
    const cpm = impressions > 0 ? (spend / impressions) * 1000 : 0;
    const cpc = clicks > 0 ? spend / clicks : 0;
    const cpe = engagement > 0 ? spend / engagement : 0;
    const cpl = linkClicks > 0 ? spend / linkClicks : 0;
    const cpmsg = msgStarts > 0 ? spend / msgStarts : 0;
    const cpa = purchases > 0 ? spend / purchases : 0;
    
    // Define funnel stages with 3D colors
    const maxMetric = Math.max(impressions, reach, engagement, Math.max(linkClicks, clicks, msgStarts), Math.max(purchases, 1));

    const funnelData = [
        {
            stageKey: 'display',
            color: '#0f3b66',
            lightColor: 'rgba(15, 59, 102, 0.85)',
            widthValue: impressions,
            header: 'Impressions',
            lines: [
                { label: 'Impressions', value: impressions },
                { label: 'Reach', value: reach }
            ],
            right: [
                { label: 'CPM', value: cpm, decimals: 1, hint: 'Hiển thị' }
            ]
        },
        {
            stageKey: 'engagement',
            color: '#07869b',
            lightColor: 'rgba(7, 134, 155, 0.85)',
            widthValue: engagement,
            header: 'Post Engagement',
            lines: [
                { label: 'Post Engagement', value: engagement }
            ],
            right: [
                { label: 'Cost per Post Engagement', value: cpe, decimals: 2, hint: 'Tương tác' }
            ]
        },
        {
            stageKey: 'interest',
            color: '#e6a500',
            lightColor: 'rgba(230, 165, 0, 0.9)',
            widthValue: Math.max(linkClicks, clicks, msgStarts),
            header: 'Interest',
            lines: [
                { label: 'Link Clicks', value: linkClicks },
                { label: 'Clicks', value: clicks },
                { label: 'Messaging Starts', value: msgStarts }
            ],
            right: [
                { label: 'CPC', value: cpc, decimals: 1, hint: 'Quan tâm' },
                { label: 'Cost per Message', value: cpmsg, decimals: 1 }
            ]
        },
        {
            stageKey: 'conversion',
            color: '#d94a4a',
            lightColor: 'rgba(217, 74, 74, 0.9)',
            widthValue: Math.max(purchases, 1),
            header: 'Purchases',
            lines: [
                { label: 'Purchases', value: purchases }
            ],
            right: [
                { label: 'CPA', value: cpa, decimals: 1, hint: 'Chuyển đổi' }
            ]
        }
    ];
    
    // Create custom funnel chart using HTML/CSS
    const funnelContainer = document.getElementById('funnelChart');
    funnelContainer.innerHTML = `
        <div class="funnel-container" style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px;">
            <div class="funnel-header" style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 20px;">
                <span style="font-weight: 600; color: #374151;">Đã chi tiêu</span>
                <span style="font-weight: 600; color: #374151;">Total Cost ${VND_FMT.format(spend)}</span>
            </div>
            ${funnelData.map((stage, index) => {
                const width = Math.max(25, (stage.widthValue / Math.max(maxMetric, 1)) * 100);
                return `
                    <div class="funnel-stage" style="display: flex; align-items: center; width: 100%; margin-bottom: 12px;">
                        <div class="funnel-segment" style="
                            width: ${width}%;
                            height: 60px;
                            background: linear-gradient(135deg, ${stage.color}, ${stage.lightColor});
                            border-radius: 8px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-weight: bold;
                            text-align: center;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                            position: relative;
                            overflow: hidden;
                        ">
                            <div style="
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                height: 30%;
                                background: linear-gradient(to bottom, rgba(255,255,255,0.2), transparent);
                            "></div>
                            <div style="z-index: 1; line-height: 1.2;">
                                <div style="font-size: 14px; margin-bottom: 2px;">${stage.header}</div>
                                ${stage.lines.map(l=>`<div style=\"font-size:16px; font-weight:700;\">${l.label}: ${NUM_FMT.format(parseInt(l.value||0))}</div>`).join('')}
                            </div>
                        </div>
                        <div class="cost-metrics" style="
                            margin-left: 20px;
                            text-align: left;
                            min-width: 200px;
                        ">
                            ${stage.right.map(r=>`
                                <div style=\"display:flex; align-items:center; gap:10px; margin-bottom:4px;\">
                                    <div>
                                        <div style=\"font-size:12px; color:#6b7280;\">${r.label}</div>
                                        <div style=\"font-size:14px; font-weight:600; color:#374151;\">${(r.value||0).toFixed(r.decimals ?? 1)}</div>
                                    </div>
                                    ${r.hint?`<div style=\"font-size:12px; color:#374151; margin-left:10px; white-space:nowrap;\">${r.hint}</div>`:''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}
