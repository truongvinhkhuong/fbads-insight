#!/usr/bin/env python3
"""
Flask Backend cho Facebook Ads Dashboard và Chatbot
Xử lý yêu cầu API OpenAI và phục vụ dữ liệu
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import requests

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

class OpenAIChatbot:
    """Class để xử lý tương tác với OpenAI API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY không được cấu hình")
    
    def ask_question(self, question: str, ads_data: Dict[str, Any]) -> str:
        """Gửi câu hỏi đến OpenAI API với context dữ liệu quảng cáo"""
        if not self.api_key:
            return "Xin lỗi, API key chưa được cấu hình. Vui lòng kiểm tra cài đặt."
        
        try:
            # Tạo prompt với context dữ liệu
            system_prompt = """Bạn là một chuyên gia phân tích quảng cáo Facebook. 
            Dựa trên dữ liệu quảng cáo được cung cấp, hãy trả lời câu hỏi của người dùng một cách ngắn gọn và chính xác.
            Chỉ sử dụng thông tin có trong dữ liệu được cung cấp."""
            
            user_prompt = f"""Dữ liệu quảng cáo Facebook:
            {json.dumps(ads_data, ensure_ascii=False, indent=2)}
            
            Câu hỏi: {question}
            
            Hãy trả lời dựa trên dữ liệu trên."""
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            answer = result['choices'][0]['message']['content']
            
            logger.info(f"OpenAI API response: {answer}")
            return answer
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi API OpenAI: {e}")
            return f"Xin lỗi, có lỗi khi kết nối đến OpenAI API: {str(e)}"
        except Exception as e:
            logger.error(f"Lỗi không mong muốn: {e}")
            return "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu."

def load_ads_data() -> Dict[str, Any]:
    """Tải dữ liệu quảng cáo từ file JSON"""
    try:
        with open('ads_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.warning("File ads_data.json không tìm thấy, trả về dữ liệu mẫu")
        return {
            'extraction_date': datetime.now().isoformat(),
            'campaigns': [],
            'message': 'Dữ liệu mẫu - chưa có dữ liệu thực'
        }
    except Exception as e:
        logger.error(f"Lỗi khi đọc file dữ liệu: {e}")
        return {'error': f'Lỗi đọc dữ liệu: {str(e)}'}

@app.route('/')
def index():
    """Trang chủ dashboard"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ads-data')
def get_ads_data():
    """API endpoint để lấy dữ liệu quảng cáo"""
    try:
        data = load_ads_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """API endpoint để xử lý câu hỏi từ chatbot"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Câu hỏi không được để trống'}), 400
        
        # Tải dữ liệu quảng cáo
        ads_data = load_ads_data()
        
        # Khởi tạo chatbot
        chatbot = OpenAIChatbot()
        
        # Gửi câu hỏi
        answer = chatbot.ask_question(question, ads_data)
        
        return jsonify({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi xử lý câu hỏi: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'openai_configured': bool(os.getenv('OPENAI_API_KEY'))
    })

# HTML Template cho dashboard
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Ads Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .chatbot-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        .chatbot-container {
            position: fixed;
            bottom: 80px;
            right: 20px;
            z-index: 999;
            display: none;
        }
        .chatbot-messages {
            max-height: 400px;
            overflow-y: auto;
        }
        .message {
            margin: 8px 0;
            padding: 8px 12px;
            border-radius: 8px;
        }
        .user-message {
            background-color: #247ba0;
            color: white;
            margin-left: 20px;
        }
        .bot-message {
            background-color: #f3f4f6;
            color: #374151;
            margin-right: 20px;
        }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">Facebook Ads Dashboard</h1>
                    <p class="text-gray-600">Phân tích hiệu suất quảng cáo Facebook</p>
                </div>
                <div class="text-right">
                    <p class="text-sm text-gray-500">Cập nhật lần cuối:</p>
                    <p id="last-update" class="text-sm font-medium text-gray-900">Đang tải...</p>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 rounded-md flex items-center justify-center" style="background-color:#247ba0;">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                        </div>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-gray-500 truncate">Tổng Impressions</dt>
                            <dd id="total-impressions" class="text-lg font-medium text-gray-900">0</dd>
                        </dl>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                            </svg>
                        </div>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-gray-500 truncate">Tổng Clicks</dt>
                            <dd id="total-clicks" class="text-lg font-medium text-gray-900">0</dd>
                        </dl>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                            </svg>
                        </div>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-gray-500 truncate">Tổng Spend</dt>
                            <dd id="total-spend" class="text-lg font-medium text-gray-900">$0</dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <!-- Impressions Chart -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Impressions theo Chiến dịch</h3>
                <canvas id="impressionsChart" width="400" height="200"></canvas>
            </div>

            <!-- Clicks Chart -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Clicks theo Chiến dịch</h3>
                <canvas id="clicksChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- Spend Chart -->
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Phân bổ Spend theo Chiến dịch</h3>
            <div class="flex justify-center">
                <canvas id="spendChart" width="400" height="300"></canvas>
            </div>
        </div>

        <!-- Campaigns Table -->
        <div class="bg-white rounded-lg shadow mt-8">
            <div class="px-6 py-4 border-b border-gray-200">
                <h3 class="text-lg font-medium text-gray-900">Danh sách Chiến dịch</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tên Chiến dịch</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mục tiêu</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Impressions</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Clicks</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Spend</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CTR</th>
                        </tr>
                    </thead>
                    <tbody id="campaigns-table" class="bg-white divide-y divide-gray-200">
                        <!-- Campaigns will be populated here -->
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <!-- Chatbot Toggle Button -->
    <button id="chatbot-toggle" class="chatbot-toggle text-white rounded-full p-4 shadow-lg transition-colors duration-200" style="background-color:#247ba0;">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
        </svg>
    </button>

    <!-- Chatbot Container -->
    <div id="chatbot-container" class="chatbot-container bg-white rounded-lg shadow-lg w-80">
        <div class="text-white px-4 py-3 rounded-t-lg" style="background-color:#247ba0;">
            <h3 class="font-medium">Facebook Ads Assistant</h3>
            <p class="text-sm opacity-90">Hỏi tôi về dữ liệu quảng cáo</p>
        </div>
        
        <div class="p-4">
            <div id="chatbot-messages" class="chatbot-messages mb-4">
                <div class="message bot-message">
                    Xin chào! Tôi có thể giúp bạn phân tích dữ liệu quảng cáo Facebook. Hãy hỏi tôi bất kỳ câu hỏi nào!
                </div>
            </div>
            
            <div class="flex space-x-2">
                <input type="text" id="chatbot-input" placeholder="Nhập câu hỏi..." 
                       class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none">
                <button id="chatbot-send" class="px-4 py-2 text-white rounded-md" style="background-color:#247ba0;">
                    Gửi
                </button>
            </div>
            
            <div class="mt-3 text-xs text-gray-500">
                <p>Ví dụ: "Chiến dịch nào có impressions cao nhất?"</p>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let adsData = null;
        let charts = {};

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadAdsData();
            initializeChatbot();
        });

        // Load ads data
        async function loadAdsData() {
            try {
                const response = await fetch('/api/ads-data');
                adsData = await response.json();
                
                if (adsData.error) {
                    console.error('Error loading data:', adsData.error);
                    return;
                }
                
                updateDashboard(adsData);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        // Update dashboard with data
        function updateDashboard(data) {
            // Update last update time
            const lastUpdate = document.getElementById('last-update');
            if (data.extraction_date) {
                const date = new Date(data.extraction_date);
                lastUpdate.textContent = date.toLocaleString('vi-VN');
            }

            // Calculate totals
            let totalImpressions = 0;
            let totalClicks = 0;
            let totalSpend = 0;

            data.campaigns.forEach(campaign => {
                if (campaign.insights && campaign.insights.impressions) {
                    totalImpressions += parseInt(campaign.insights.impressions) || 0;
                }
                if (campaign.insights && campaign.insights.clicks) {
                    totalClicks += parseInt(campaign.insights.clicks) || 0;
                }
                if (campaign.insights && campaign.insights.spend) {
                    totalSpend += parseFloat(campaign.insights.spend) || 0;
                }
            });

            // Update stats cards
            document.getElementById('total-impressions').textContent = totalImpressions.toLocaleString();
            document.getElementById('total-clicks').textContent = totalClicks.toLocaleString();
            document.getElementById('total-spend').textContent = '$' + totalSpend.toLocaleString();

            // Update campaigns table
            updateCampaignsTable(data.campaigns);

            // Create charts
            createCharts(data.campaigns);
        }

        // Update campaigns table
        function updateCampaignsTable(campaigns) {
            const tbody = document.getElementById('campaigns-table');
            tbody.innerHTML = '';

            campaigns.forEach(campaign => {
                const row = document.createElement('tr');
                const insights = campaign.insights || {};
                
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${campaign.campaign_name}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${campaign.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                            ${campaign.status}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${campaign.objective}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${insights.impressions || '0'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${insights.clicks || '0'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${insights.spend || '0.00'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${insights.ctr || '0.00'}%</td>
                `;
                
                tbody.appendChild(row);
            });
        }

        // Create charts
        function createCharts(campaigns) {
            const campaignNames = campaigns.map(c => c.campaign_name);
            const impressions = campaigns.map(c => parseInt(c.insights?.impressions || 0));
            const clicks = campaigns.map(c => parseInt(c.insights?.clicks || 0));
            const spend = campaigns.map(c => parseFloat(c.insights?.spend || 0));

            // Impressions Chart (Bar)
            const impressionsCtx = document.getElementById('impressionsChart').getContext('2d');
            charts.impressions = new Chart(impressionsCtx, {
                type: 'bar',
                data: {
                    labels: campaignNames,
                    datasets: [{
                        label: 'Impressions',
                        data: impressions,
                        backgroundColor: '#247ba0',
                        borderColor: '#247ba0',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Clicks Chart (Line)
            const clicksCtx = document.getElementById('clicksChart').getContext('2d');
            charts.clicks = new Chart(clicksCtx, {
                type: 'line',
                data: {
                    labels: campaignNames,
                    datasets: [{
                        label: 'Clicks',
                        data: clicks,
                        borderColor: '#247ba0',
                        backgroundColor: 'rgba(36, 123, 160, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Spend Chart (Doughnut)
            const spendCtx = document.getElementById('spendChart').getContext('2d');
            charts.spend = new Chart(spendCtx, {
                type: 'doughnut',
                data: {
                    labels: campaignNames,
                    datasets: [{
                        data: spend,
                        backgroundColor: [
                            '#247ba0',
                            '#3b82f6',
                            '#10b981',
                            '#f59e0b',
                            '#ef4444'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // Initialize chatbot
        function initializeChatbot() {
            const toggleBtn = document.getElementById('chatbot-toggle');
            const container = document.getElementById('chatbot-container');
            const input = document.getElementById('chatbot-input');
            const sendBtn = document.getElementById('chatbot-send');

            // Toggle chatbot
            toggleBtn.addEventListener('click', () => {
                container.style.display = container.style.display === 'none' ? 'block' : 'none';
            });

            // Send message
            function sendMessage() {
                const question = input.value.trim();
                if (!question) return;

                // Add user message
                addMessage(question, 'user');
                input.value = '';

                // Show loading
                addMessage('Đang xử lý...', 'bot');

                // Send to API
                fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: question })
                })
                .then(response => response.json())
                .then(data => {
                    // Remove loading message
                    removeLastMessage();
                    
                    if (data.error) {
                        addMessage('Xin lỗi, có lỗi xảy ra: ' + data.error, 'bot');
                    } else {
                        addMessage(data.answer, 'bot');
                    }
                })
                .catch(error => {
                    removeLastMessage();
                    addMessage('Xin lỗi, có lỗi kết nối. Vui lòng thử lại.', 'bot');
                });
            }

            // Event listeners
            sendBtn.addEventListener('click', sendMessage);
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }

        // Add message to chatbot
        function addMessage(text, type) {
            const messagesContainer = document.getElementById('chatbot-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Remove last message
        function removeLastMessage() {
            const messagesContainer = document.getElementById('chatbot-messages');
            const messages = messagesContainer.querySelectorAll('.message');
            if (messages.length > 0) {
                messages[messages.length - 1].remove();
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Khởi động Flask app trên port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
