// JavaScript for Daily Tracking functionality

let dailyTrackingData = null;

function initializeDailyTracking() {
    // Load initial data
    loadDailyTrackingData();
    
    // Event listeners
    document.getElementById('btn-refresh-daily').addEventListener('click', loadDailyTrackingData);
    document.getElementById('btn-export-daily').addEventListener('click', exportDailyData);
    document.getElementById('daily-date-preset').addEventListener('change', loadDailyTrackingData);
}

async function refreshBudgetCache() {
    try {
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = 'Đang cập nhật...';
        button.disabled = true;
        
        const response = await fetch('/api/refresh-budgets');
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Cập nhật thành công!\n- ${data.updated_count} campaigns được cập nhật\n- ${data.failed_count} campaigns thất bại\n\nCache sẽ được sử dụng trong 1 giờ tới.`);
            // Reload daily tracking data to show updated budget info
            loadDailyTrackingData();
        } else {
            alert(`❌ Lỗi: ${data.error}`);
        }
    } catch (error) {
        console.error('Error refreshing budget cache:', error);
        alert('❌ Lỗi kết nối khi cập nhật ngân sách');
    } finally {
        button.textContent = 'Cập nhật Ngân sách';
        button.disabled = false;
    }
}

async function loadDailyTrackingData() {
    try {
        const preset = document.getElementById('daily-date-preset').value || 'last_7d';
        const tbody = document.getElementById('daily-tracking-table');
        tbody.innerHTML = '<tr><td colspan="24" class="px-6 py-4 text-center text-gray-500">Đang tải dữ liệu...</td></tr>';
        
        const response = await fetch(`/api/daily-tracking?date_preset=${encodeURIComponent(preset)}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('Daily tracking error:', data.error);
            let errorMessage = data.error;
            if (typeof data.error === 'object' && data.error.message) {
                errorMessage = data.error.message;
            }
            
            // Check for token expiration
            if (errorMessage.includes('expired') || errorMessage.includes('Session has expired')) {
                errorMessage = 'Token Facebook đã hết hạn. Vui lòng cập nhật token mới trong file .env';
            }
            
            tbody.innerHTML = `<tr><td colspan="24" class="px-6 py-4 text-center text-red-500">Lỗi: ${errorMessage}</td></tr>`;
            return;
        }
        
        dailyTrackingData = data;
        updateDailyTrackingTable(data);
        updateDailySummaryCards(data);
        
        // Show campaign status
        const statusEl = document.getElementById('campaign-status');
        if (data.total_campaigns > 0) {
            let statusText = `Đã tải ${data.successful_campaigns}/${data.processed_campaigns || data.total_campaigns} chiến dịch`;
            if (data.note) {
                statusText += ` (${data.note})`;
            }
            statusEl.textContent = statusText;
            statusEl.classList.remove('hidden');
            if (data.failed_campaigns > 0) {
                statusEl.classList.add('text-yellow-600');
                statusEl.classList.remove('text-blue-600');
            } else {
                statusEl.classList.add('text-green-600');
                statusEl.classList.remove('text-blue-600');
            }
        } else {
            statusEl.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error loading daily tracking data:', error);
        const tbody = document.getElementById('daily-tracking-table');
        let errorMessage = 'Lỗi kết nối khi tải dữ liệu';
        
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            errorMessage = 'Lỗi timeout - Dữ liệu quá lớn, vui lòng thử lại với date range nhỏ hơn';
        } else if (error.message.includes('timeout')) {
            errorMessage = 'Lỗi timeout - Vui lòng thử lại';
        }
        
        tbody.innerHTML = `<tr><td colspan="24" class="px-6 py-4 text-center text-red-500">${errorMessage}</td></tr>`;
    }
}

function updateDailyTrackingTable(data) {
    const tbody = document.getElementById('daily-tracking-table');
    tbody.innerHTML = '';
    
    if (!data.daily || data.daily.length === 0) {
        tbody.innerHTML = '<tr><td colspan="24" class="px-6 py-4 text-center text-gray-500">Không có dữ liệu</td></tr>';
        return;
    }
    
    data.daily.forEach(day => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        // Calculate metrics
        const spend = parseFloat(day.spend || 0);
        const reach = parseInt(day.reach || 0);
        const impressions = parseInt(day.impressions || 0);
        const clicks = parseInt(day.clicks || 0);
        const linkClicks = parseInt(day.inline_link_clicks || 0);
        const engagement = parseInt(day.post_engagement || 0);
        const messagingStarts = parseInt(day.messaging_starts || 0);
        const purchases = parseInt(day.purchases || 0);
        const purchaseValue = parseFloat(day.purchase_value || 0);
        const frequency = parseFloat(day.frequency || 0);
        const videoViews = parseInt(day.video_views || 0);
        
        // Calculate derived metrics
        const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
        const linkCtr = impressions > 0 ? (linkClicks / impressions) * 100 : 0;
        const cpc = clicks > 0 ? spend / clicks : 0;
        const linkCpc = linkClicks > 0 ? spend / linkClicks : 0;
        const cpm = impressions > 0 ? (spend / impressions) * 1000 : 0;
        const cpe = engagement > 0 ? spend / engagement : 0;
        const roas = spend > 0 ? purchaseValue / spend : 0;
        
        // Determine result based on objective (simplified)
        const result = linkClicks > 0 ? `${linkClicks} Link Clicks` : 
                      engagement > 0 ? `${engagement} Engagement` : 
                      `${clicks} Clicks`;
        
        const photoViews = parseInt(day.photo_view || 0);
        const video2sPlus = parseInt(day.video_2_sec_watched_actions || 0);
        const campaignCount = parseInt(day.campaign_count || 0);
        
        // Budget calculations
        const dailyBudget = parseFloat(day.daily_budget || 0);
        const lifetimeBudget = parseFloat(day.lifetime_budget || 0);
        const budgetRemaining = parseFloat(day.budget_remaining || 0);
        const totalBudget = dailyBudget + lifetimeBudget;
        const budgetUtilization = totalBudget > 0 ? (spend / totalBudget) * 100 : 0;
        
        row.innerHTML = `
            <td class="px-2 py-3 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                ${new Date(day.date_start || day.date).toLocaleDateString('vi-VN')}
            </td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-500">-</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900 font-medium">${VND_FMT.format(spend)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${totalBudget > 0 ? VND_FMT.format(totalBudget) : (budgetRemaining > 0 ? `Remaining: ${VND_FMT.format(budgetRemaining)}` : '-')}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(reach)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(impressions)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${frequency.toFixed(2)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${result}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(cpc)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(messagingStarts)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(purchases)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${roas.toFixed(2)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${ctr.toFixed(2)}%</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(cpm)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(engagement)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(linkClicks)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${linkCtr.toFixed(2)}%</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(linkCpc)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(videoViews)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(photoViews)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(cpe)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(video2sPlus)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(purchaseValue)}</td>
            <td class="px-2 py-3 whitespace-nowrap text-sm text-gray-900">${campaignCount}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function updateDailySummaryCards(data) {
    if (!data.totals) return;
    
    const totals = data.totals;
    const spend = parseFloat(totals.spend || 0);
    const reach = parseInt(totals.reach || 0);
    const impressions = parseInt(totals.impressions || 0);
    const clicks = parseInt(totals.clicks || 0);
    const linkClicks = parseInt(totals.inline_link_clicks || 0);
    const engagement = parseInt(totals.post_engagement || 0);
    const messagingStarts = parseInt(totals.messaging_starts || 0);
    const purchases = parseInt(totals.purchases || 0);
    const purchaseValue = parseFloat(totals.purchase_value || 0);
    
    // Calculate averages
    const avgCtr = impressions > 0 ? (clicks / impressions) * 100 : 0;
    const avgCpc = clicks > 0 ? spend / clicks : 0;
    const avgCpm = impressions > 0 ? (spend / impressions) * 1000 : 0;
    const avgRoas = spend > 0 ? purchaseValue / spend : 0;
    
    // Update summary cards
    document.getElementById('daily-total-spend').textContent = VND_FMT.format(spend);
    document.getElementById('daily-total-reach').textContent = NUM_FMT.format(reach);
    document.getElementById('daily-total-impressions').textContent = NUM_FMT.format(impressions);
    document.getElementById('daily-avg-ctr').textContent = avgCtr.toFixed(2) + '%';
    document.getElementById('daily-avg-cpc').textContent = VND_FMT.format(avgCpc);
    document.getElementById('daily-avg-cpm').textContent = VND_FMT.format(avgCpm);
    
    // Update summary section
    document.getElementById('summary-total-spend').textContent = VND_FMT.format(spend);
    document.getElementById('summary-total-reach').textContent = NUM_FMT.format(reach);
    document.getElementById('summary-total-impressions').textContent = NUM_FMT.format(impressions);
    document.getElementById('summary-avg-ctr').textContent = avgCtr.toFixed(2) + '%';
    document.getElementById('summary-avg-cpc').textContent = VND_FMT.format(avgCpc);
    document.getElementById('summary-avg-cpm').textContent = VND_FMT.format(avgCpm);
    document.getElementById('summary-total-messaging').textContent = NUM_FMT.format(messagingStarts);
    document.getElementById('summary-total-conversions').textContent = NUM_FMT.format(purchases);
    document.getElementById('summary-avg-roas').textContent = avgRoas.toFixed(2);
}

function exportDailyData() {
    if (!dailyTrackingData || !dailyTrackingData.daily) {
        alert('Không có dữ liệu để export');
        return;
    }
    
    const rows = dailyTrackingData.daily.map(day => {
        const spend = parseFloat(day.spend || 0);
        const reach = parseInt(day.reach || 0);
        const impressions = parseInt(day.impressions || 0);
        const clicks = parseInt(day.clicks || 0);
        const linkClicks = parseInt(day.inline_link_clicks || 0);
        const engagement = parseInt(day.post_engagement || 0);
        const messagingStarts = parseInt(day.messaging_starts || 0);
        const purchases = parseInt(day.purchases || 0);
        const purchaseValue = parseFloat(day.purchase_value || 0);
        const frequency = parseFloat(day.frequency || 0);
        const videoViews = parseInt(day.video_views || 0);
        const photoViews = parseInt(day.photo_view || 0);
        const video2sPlus = parseInt(day.video_2_sec_watched_actions || 0);
        const campaignCount = parseInt(day.campaign_count || 0);
        
        const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
        const linkCtr = impressions > 0 ? (linkClicks / impressions) * 100 : 0;
        const cpc = clicks > 0 ? spend / clicks : 0;
        const linkCpc = linkClicks > 0 ? spend / linkClicks : 0;
        const cpm = impressions > 0 ? (spend / impressions) * 1000 : 0;
        const cpe = engagement > 0 ? spend / engagement : 0;
        const roas = spend > 0 ? purchaseValue / spend : 0;
        
        return {
            'Ngày': new Date(day.date_start || day.date).toLocaleDateString('vi-VN'),
            'Phân phối': '-',
            'Tổng chi tiêu': spend,
            'Ngân sách': '-',
            'Reach': reach,
            'Impressions': impressions,
            'Tần suất': frequency,
            'Kết quả': linkClicks > 0 ? `${linkClicks} Link Clicks` : engagement > 0 ? `${engagement} Engagement` : `${clicks} Clicks`,
            'CPC': cpc,
            'Messaging Starts': messagingStarts,
            'Conversions': purchases,
            'ROAS': roas,
            'CTR': ctr,
            'CPM': cpm,
            'Engagement': engagement,
            'Link Clicks': linkClicks,
            'Link CTR': linkCtr,
            'Link CPC': linkCpc,
            'Video Views': videoViews,
            'Photo Views': photoViews,
            'CPE': cpe,
            'Video 2s+': video2sPlus,
            'Purchase Value': purchaseValue,
            'Campaigns': campaignCount
        };
    });
    
    const csv = toCSV(rows);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `daily-tracking-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}
