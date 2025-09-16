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
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

def get_access_token() -> str:
    token = os.getenv('USER_TOKEN') or os.getenv('FACEBOOK_ACCESS_TOKEN')
    return token or ''

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
    return render_template('index.html')

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

@app.route('/api/campaign-insights')
def api_campaign_insights():
    """Lấy insights theo campaign (on-demand)"""
    try:
        campaign_id = request.args.get('campaign_id', '').strip()
        since = request.args.get('since')
        until = request.args.get('until')
        status = request.args.get('status', '').upper()
        if not campaign_id:
            return jsonify({'error': 'campaign_id is required'}), 400
        token = get_access_token()
        if not token:
            return jsonify({'error': 'Missing access token'}), 500

        base_url = 'https://graph.facebook.com/v23.0'
        url = f"{base_url}/{campaign_id}/insights"
        def fetch(params):
            r = requests.get(url, params=params, timeout=30)
            return r.status_code, r.json()

        # Strategy 1: for ACTIVE, thử gần nhất; cho STOPPED, thử 30-90d
        params = {
            'access_token': token,
            'fields': 'campaign_name,impressions,clicks,spend,ctr,cpc,cpm,reach,frequency',
            'date_preset': 'last_7d' if status == 'ACTIVE' else 'last_30d',
            'time_increment': 1
        }
        if since and until:
            params['date_preset'] = 'custom'
            params['since'] = since
            params['until'] = until

        status, data = fetch(params)
        if status != 200:
            return jsonify({'error': data.get('error', {'message': 'Unknown error'})}), status
        rows = data.get('data', [])

        # Strategy 2: if empty, broaden window
        if not rows:
            params2 = params.copy()
            params2['date_preset'] = 'last_14d' if status == 'ACTIVE' else 'last_90d'
            status, data = fetch(params2)
            if status == 200:
                rows = data.get('data', [])

        # Strategy 3: if still empty, try yesterday/today for ACTIVE
        if not rows and status == 'ACTIVE':
            for preset in ['yesterday', 'today']:
                params3a = params.copy()
                params3a['date_preset'] = preset
                status_code, data = fetch(params3a)
                if status_code == 200:
                    rows = data.get('data', [])
                    if rows:
                        break

        # Strategy 4: if still empty, try lifetime without time_increment
        if not rows:
            params3 = {
                'access_token': token,
                'fields': 'campaign_name,impressions,clicks,spend,ctr,cpc,cpm,reach,frequency',
                'date_preset': 'lifetime'
            }
            status, data = fetch(params3)
            if status == 200:
                rows = data.get('data', [])
        # Tổng hợp nhanh
        totals = {
            'impressions': 0,
            'clicks': 0,
            'spend': 0.0,
            'reach': 0,
        }
        for r in rows:
            totals['impressions'] += int(float(r.get('impressions', 0) or 0))
            totals['clicks'] += int(float(r.get('clicks', 0) or 0))
            totals['spend'] += float(r.get('spend', 0) or 0)
            totals['reach'] += int(float(r.get('reach', 0) or 0))

        return jsonify({'totals': totals, 'daily': rows})
    except Exception as e:
        logger.error(f"Lỗi /api/campaign-insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign-breakdown')
def api_campaign_breakdown():
    """Insights breakdown theo placement/age-gender/country"""
    try:
        campaign_id = request.args.get('campaign_id', '').strip()
        kind = request.args.get('kind', 'placement')  # placement | age_gender | country
        date_preset = request.args.get('date_preset', 'last_30d')
        if not campaign_id:
            return jsonify({'error': 'campaign_id is required'}), 400
        token = get_access_token()
        base_url = 'https://graph.facebook.com/v23.0'
        breakdowns = {
            'placement': 'placement',
            'age_gender': 'age,gender',
            'country': 'country'
        }.get(kind, 'placement')
        params = {
            'access_token': token,
            'fields': 'impressions,clicks,spend,ctr,cpc,cpm',
            'breakdowns': breakdowns,
            'date_preset': date_preset
        }
        res = requests.get(f"{base_url}/{campaign_id}/insights", params=params, timeout=30)
        data = res.json()
        rows = []
        if res.status_code == 200:
            rows = data.get('data', [])
        else:
            # Fallback cho placement: thử publisher_platform + platform_position
            if kind == 'placement':
                fb_params = params.copy()
                fb_params['breakdowns'] = 'publisher_platform,platform_position'
                res2 = requests.get(f"{base_url}/{campaign_id}/insights", params=fb_params, timeout=30)
                if res2.status_code == 200:
                    rows_raw = res2.json().get('data', [])
                    # Gộp nhãn thành placement-like
                    for r in rows_raw:
                        r['placement'] = f"{r.get('publisher_platform','')}:{r.get('platform_position','')}"
                    rows = rows_raw
                else:
                    return jsonify({'error': data.get('error', {'message': 'Unknown error'})}), res.status_code
            else:
                return jsonify({'error': data.get('error', {'message': 'Unknown error'})}), res.status_code
        return jsonify({'rows': rows})
    except Exception as e:
        logger.error(f"Lỗi /api/campaign-breakdown: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign-ads')
def api_campaign_ads():
    """Danh sách ads + insights cơ bản theo campaign"""
    try:
        campaign_id = request.args.get('campaign_id', '').strip()
        date_preset = request.args.get('date_preset', 'last_30d')
        if not campaign_id:
            return jsonify({'error': 'campaign_id is required'}), 400
        token = get_access_token()
        base_url = 'https://graph.facebook.com/v23.0'

        # list ads under campaign
        ads_res = requests.get(f"{base_url}/{campaign_id}/ads", params={'access_token': token, 'fields': 'id,name,status,created_time', 'limit': 50}, timeout=30)
        ads_data = ads_res.json()
        if ads_res.status_code != 200:
            return jsonify({'error': ads_data.get('error', {'message': 'Unknown error'})}), ads_res.status_code
        ads = ads_data.get('data', [])

        # fetch insights per ad (lightweight)
        result = []
        for ad in ads[:20]:
            ins_params = {
                'access_token': token,
                'fields': 'impressions,clicks,spend,ctr,cpc,cpm,reach',
                'date_preset': date_preset
            }
            ins_res = requests.get(f"{base_url}/{ad['id']}/insights", params=ins_params, timeout=30)
            ins = ins_res.json().get('data', []) if ins_res.status_code == 200 else []
            result.append({'ad': ad, 'insights': ins[0] if ins else {}})

        return jsonify({'items': result})
    except Exception as e:
        logger.error(f"Lỗi /api/campaign-ads: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Khởi động Flask app trên port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
