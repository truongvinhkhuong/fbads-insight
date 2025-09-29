// JavaScript for AI Analysis functionality

// AI Analysis Functions
async function performAIAnalysis(campaignId) {
    const aiContent = document.getElementById('ai-analysis-content');
    const aiLoading = document.getElementById('ai-loading');
    const aiError = document.getElementById('ai-error');
    const aiErrorMsg = document.getElementById('ai-error-message');
    
    // Show loading state
    aiContent.classList.add('hidden');
    aiError.classList.add('hidden');
    aiLoading.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/campaign-ai-insights', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                campaign_id: campaignId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display results với error handling
            try {
                document.getElementById('ai-insights').innerHTML = formatAIResponse(data.insights);
                document.getElementById('ai-recommendations').innerHTML = formatAIResponse(data.recommendations);
            } catch (formatError) {
                console.error('Error formatting AI response:', formatError);
                console.log('Raw insights data:', data.insights);
                console.log('Raw recommendations data:', data.recommendations);
                
                // Fallback display
                document.getElementById('ai-insights').innerHTML = `<div class="text-sm text-gray-600">
                    <strong>Insights:</strong><br>
                    ${typeof data.insights === 'string' ? data.insights : JSON.stringify(data.insights, null, 2)}
                </div>`;
                document.getElementById('ai-recommendations').innerHTML = `<div class="text-sm text-gray-600">
                    <strong>Recommendations:</strong><br>
                    ${typeof data.recommendations === 'string' ? data.recommendations : JSON.stringify(data.recommendations, null, 2)}
                </div>`;
            }
            
            // Show timestamp
            const timestamp = new Date(data.timestamp).toLocaleString('vi-VN');
            document.getElementById('ai-analysis-timestamp').textContent = `Phân tích lúc: ${timestamp}`;
            
            // Show cache indicator if cached
            const cacheIndicator = document.getElementById('ai-cache-indicator');
            if (data.cached) {
                cacheIndicator.classList.remove('hidden');
            } else {
                cacheIndicator.classList.add('hidden');
            }
            
            // Show content
            aiLoading.classList.add('hidden');
            aiContent.classList.remove('hidden');
        } else {
            throw new Error(data.error || 'Không thể phân tích AI');
        }
    } catch (error) {
        console.error('AI Analysis Error:', error);
        console.error('Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        
        aiErrorMsg.textContent = error.message || 'Có lỗi xảy ra khi phân tích AI';
        aiLoading.classList.add('hidden');
        aiError.classList.remove('hidden');
    }
}

function formatAIResponse(text) {
    if (!text) return '<em>Không có dữ liệu</em>';
    
    // Đảm bảo text là string
    let textStr = '';
    if (typeof text === 'string') {
        textStr = text;
    } else if (typeof text === 'object') {
        // Nếu là object, convert thành string
        textStr = JSON.stringify(text, null, 2);
    } else {
        textStr = String(text);
    }
    
    // Convert line breaks to HTML and add bullet points
    return textStr
        .split('\n')
        .filter(line => line.trim())
        .map(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith('-') || trimmed.startsWith('•') || trimmed.startsWith('*')) {
                return `<div class="flex items-start mb-2">
                    <span class="text-blue-600 mr-2 mt-1">-</span>
                    <span>${trimmed.substring(1).trim()}</span>
                </div>`;
            }
            return `<div class="mb-2">${trimmed}</div>`;
        })
        .join('');
}

function resetAIState() {
    document.getElementById('ai-analysis-content').classList.add('hidden');
    document.getElementById('ai-loading').classList.add('hidden');
    document.getElementById('ai-error').classList.add('hidden');
    document.getElementById('ai-cache-indicator').classList.add('hidden');
}
