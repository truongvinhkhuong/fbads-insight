#!/usr/bin/env python3

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
from facebook_ads_extractor import FacebookAdsExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

def get_access_token() -> str:
    token = os.getenv('USER_TOKEN') or os.getenv('FACEBOOK_ACCESS_TOKEN')
    return token or ''

class OpenAIChatbot:
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.cache = {}
        self.cache_ttl = timedelta(hours=2)
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY không được cấu hình")
    
    def _get_cache_key(self, data: Dict[str, Any]) -> str:
        cache_data = {
            'campaign_id': data.get('campaign_id'),
            'total_impressions': data.get('summary_metrics', {}).get('total_impressions', 0),
            'total_clicks': data.get('summary_metrics', {}).get('total_clicks', 0),
            'total_spend': data.get('summary_metrics', {}).get('total_spend', 0),
            'avg_ctr': data.get('summary_metrics', {}).get('avg_ctr', 0)
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        cache_time = datetime.fromisoformat(cache_entry['timestamp'])
        return datetime.now() - cache_time < self.cache_ttl
    
    def analyze_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, str]:
        if not self.api_key:
            return {
                'insights': 'API key chưa được cấu hình. Vui lòng kiểm tra cài đặt.',
                'recommendations': 'Không thể đưa ra đề xuất do thiếu cấu hình API.',
                'cached': False
            }
        
        cache_key = self._get_cache_key(campaign_data)
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.info(f"Sử dụng cache cho campaign analysis: {cache_key[:8]}...")
                return {
                    'insights': cache_entry['insights'],
                    'recommendations': cache_entry['recommendations'],
                    'cached': True
                }
            else:
                del self.cache[cache_key]
        
        try:
            optimized_data = self._optimize_data_for_ai(campaign_data)
            
            system_prompt = (
                "Bạn là một Chuyên gia Phân tích Dữ liệu Quảng cáo và Chuyên gia Tối ưu hóa Hiệu suất có 10 năm kinh nghiệm. Bạn có kiến thức chuyên sâu về nền tảng Meta Ads, các chỉ số cốt lõi, và các framework chẩn đoán vấn đề hiệu quả. Nhiệm vụ của bạn là biến dữ liệu thô của một chiến dịch quảng cáo thành các phát hiện quan trọng và các đề xuất hành động cụ thể.\n\n"
                
                "Phân tích toàn diện dữ liệu của một chiến dịch quảng cáo Meta Ads đã hoàn thành hoặc đang chạy, với các mục tiêu sau:\n"
                "1. Chẩn đoán vấn đề: Xác định các vấn đề hiệu suất chính dựa trên các chỉ số cốt lõi.\n"
                "2. Tìm kiếm phát hiện: Khám phá các xu hướng và mối quan hệ nhân quả trong dữ liệu.\n"
                "3. Đề xuất hành động: Cung cấp các kế hoạch hành động cụ thể, có thể thực thi ngay lập tức để tối ưu hóa hiệu suất chiến dịch trong tương lai.\n\n"
                
                "Dữ liệu sẽ được cung cấp dưới dạng bảng, bao gồm các cột chỉ số và kích thước sau:\n"
                "- Kích thước: Campaign Name, Ad Set Name, Ad Name.\n"
                "- Chỉ số: Amount Spent, Impressions, Reach, Frequency, Link Clicks, Outbound Clicks, CTR (Link Click-Through Rate), CPC (Cost per Link Click), CPM, Conversions, Cost Per Conversion (CPA), Total Conversion Value, ROAS (Return on Ad Spend).\n"
                "Ngoài ra, tôi sẽ cung cấp bối cảnh chiến dịch, bao gồm:\n"
                "- Mục tiêu chính của chiến dịch: [Điền mục tiêu]\n"
                "- Ngân sách chiến dịch: [Điền ngân sách]\n"
                "- Đối tượng mục tiêu: [Điền mô tả đối tượng]\n"
                "- Khoảng thời gian chạy: [Điền thời gian]\n\n"
                
                "Sử dụng các bước sau để phân tích:\n"
                "1. **Phân tích Cấp Chiến dịch (Campaign Level):** Đánh giá hiệu suất tổng thể của chiến dịch dựa trên CPA và ROAS. So sánh các chỉ số này với mục tiêu ban đầu của chiến dịch.\n"
                "2. **Phân tích Cấp Nhóm quảng cáo (Ad Set Level):** Chẩn đoán các vấn đề liên quan đến đối tượng và ngân sách. So sánh các chỉ số CPA và ROAS giữa các nhóm quảng cáo khác nhau. Xác định nhóm quảng cáo hoạt động tốt nhất và kém nhất. Phân tích chỉ số Frequency của từng nhóm quảng cáo.\n"
                "3. **Phân tích Cấp Quảng cáo (Ad Level):** Đánh giá hiệu suất của nội dung quảng cáo (Creative). So sánh các chỉ số CTR và CPC giữa các quảng cáo trong cùng một nhóm quảng cáo. Xác định các quảng cáo hiệu quả nhất và kém hiệu quả nhất.\n"
                "4. **Chẩn đoán Mối Quan Hệ:** Thiết lập mối quan hệ nhân quả giữa các chỉ số. Ví dụ:\n"
                "    - Nếu CPA cao và CTR thấp, vấn đề nằm ở nội dung quảng cáo hoặc đối tượng mục tiêu.\n"
                "    - Nếu CPA cao nhưng CTR cao, vấn đề có thể nằm ở trang đích hoặc tỷ lệ chuyển đổi.\n"
                "    - Nếu ROAS thấp, phân tích xem đó là do CPA cao hay giá trị đơn hàng trung bình thấp.\n\n"
                
                "- **Vấn đề `CTR` thấp:** Khi chỉ số này thấp hơn mức trung bình của ngành hoặc thấp hơn kỳ vọng của bạn, đó là dấu hiệu của nội dung không hấp dẫn hoặc nhắm sai đối tượng.\n"
                "- **Vấn đề `CPA` cao:** Khi chi phí để có một kết quả quá cao, đó là dấu hiệu của hiệu quả chuyển đổi kém hoặc chi phí đấu thầu cao.\n"
                "- **Vấn đề `ROAS` thấp:** Khi lợi nhuận trên chi tiêu quảng cáo không đạt mục tiêu, đó là dấu hiệu của hiệu suất tài chính kém.\n\n"
                
                "Trình bày kết quả phân tích trong một báo cáo có cấu trúc rõ ràng, sử dụng các tiêu đề phụ và gạch đầu dòng.\n"
                "**Phần 1: Tóm Tắt Phân Tích**\n"
                "- Tóm tắt tổng thể về hiệu suất chiến dịch (tốt, trung bình, kém).\n"
                "- Các chỉ số hiệu suất chính (CPA, ROAS, CTR) so với mục tiêu.\n\n"
                
                "**Phần 2: Phân Tích Chẩn Đoán Chi Tiết**\n"
                "- Bảng Phân tích theo Cấp Nhóm quảng cáo:\n"
                "    - Liệt kê các chỉ số chính (Amount Spent, Link Clicks, CTR, CPC, CPA, ROAS, Conversions) cho từng nhóm quảng cáo.\n"
                "    - So sánh và xếp hạng các nhóm quảng cáo dựa trên ROAS và CPA.\n"
                "- Bảng Phân tích theo Cấp Quảng cáo:\n"
                "    - Liệt kê các chỉ số chính (CTR, CPC) cho từng quảng cáo.\n"
                "    - Xác định quảng cáo chiến thắng (`winner`) và quảng cáo hoạt động kém (`loser`).\n\n"
                
                "**Phần 3: Các Phát Hiện và Đề Xuất Hành Động**\n"
                "- **Đề xuất Hành động cho Nhóm quảng cáo:** Dựa trên các phát hiện ở cấp độ này, đưa ra các đề xuất cụ thể (ví dụ: tắt các nhóm quảng cáo hoạt động kém, tinh chỉnh đối tượng mục tiêu, thử nghiệm các nhóm đối tượng mới).\n"
                "- **Đề xuất Hành động cho Quảng cáo:** Dựa trên các phát hiện ở cấp độ này, đưa ra các đề xuất cụ thể (ví dụ: tắt các quảng cáo hoạt động kém, A/B testing các biến thể creative mới, làm mới nội dung để chống `ad fatigue`).\n\n"
                
                "Tạo một kế hoạch hành động cụ thể, có thể thực thi. Ví dụ:\n"
                "- `Creative Optimization`: Đề xuất A/B testing các yếu tố nào (tiêu đề, hình ảnh, video).\n"
                "- `Audience Optimization`: Đề xuất thử nghiệm các tệp đối tượng mới (ví dụ: `lookalike audience` dựa trên khách hàng giá trị cao).\n"
                "- `Bidding & Budget Strategy`: Đề xuất các thay đổi về chiến lược đấu thầu (`cost cap`, `ROAS goal`) hoặc phân bổ ngân sách.\n"
            )
            
            user_prompt = (
                f"Dữ liệu campaign (tối ưu):\n{json.dumps(optimized_data, ensure_ascii=False, indent=2)}\n\n"
                "Hãy phân tích và trả lời theo format JSON:\n"
                "{\n"
                '  "insights": "3-4 insights chính về hiệu suất campaign (CTR, CPM, trends, outliers)",\n'
                '  "recommendations": "3-4 hành động cụ thể để tối ưu hiệu suất"\n'
                "}"
            )
            
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
                'max_tokens': 600,  # Giảm từ 800 xuống 600
                'temperature': 0.3
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            answer = result['choices'][0]['message']['content']
            
            logger.info(f"OpenAI raw response length: {len(answer)} chars")
            logger.debug(f"OpenAI raw response: {answer[:500]}...")
            
            try:
                ai_response = json.loads(answer)
                insights = ai_response.get('insights', 'Không có insights')
                recommendations = ai_response.get('recommendations', 'Không có đề xuất')
                
                insights_str = str(insights) if insights else 'Không có insights'
                recommendations_str = str(recommendations) if recommendations else 'Không có đề xuất'
                
                self.cache[cache_key] = {
                    'insights': insights_str,
                    'recommendations': recommendations_str,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"AI analysis hoàn thành và cached: {cache_key[:8]}...")
                
                return {
                    'insights': insights_str,
                    'recommendations': recommendations_str,
                    'cached': False
                }
                
            except json.JSONDecodeError:
                logger.warning(f"Không thể parse JSON response từ OpenAI: {answer[:200]}...")
                fallback_response = {
                    'insights': str(answer) if answer else 'Không thể phân tích dữ liệu',
                    'recommendations': 'Vui lòng xem insights để biết thêm chi tiết.',
                    'cached': False
                }
                
                self.cache[cache_key] = {
                    'insights': fallback_response['insights'],
                    'recommendations': fallback_response['recommendations'],
                    'timestamp': datetime.now().isoformat()
                }
                
                return fallback_response
            
        except requests.exceptions.Timeout:
            logger.error("OpenAI API timeout")
            return {
                'insights': 'Lỗi timeout khi kết nối OpenAI API. Vui lòng thử lại.',
                'recommendations': "Không thể đưa ra đề xuất do lỗi timeout.",
                'cached': False
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi API OpenAI: {e}")
            return {
                'insights': f"Lỗi kết nối OpenAI API: {str(e)}",
                'recommendations': "Không thể đưa ra đề xuất do lỗi kết nối.",
                'cached': False
            }
        except Exception as e:
            logger.error(f"Lỗi không mong muốn trong AI analysis: {e}")
            return {
                'insights': f"Lỗi xử lý: {str(e)}",
                'recommendations': "Không thể đưa ra đề xuất do lỗi hệ thống.",
                'cached': False
            }
    
    def _optimize_data_for_ai(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        summary = campaign_data.get('summary_metrics', {})
        daily_trends = campaign_data.get('daily_trends', [])
        placement_breakdown = campaign_data.get('placement_breakdown', [])
        
        top_placements = sorted(placement_breakdown, 
                              key=lambda x: int(x.get('impressions', 0)), 
                              reverse=True)[:3]
        
        optimized = {
            'campaign_id': campaign_data.get('campaign_id'),
            'metrics': {
                'impressions': summary.get('total_impressions', 0),
                'clicks': summary.get('total_clicks', 0),
                'spend': round(summary.get('total_spend', 0), 2),
                'ctr': round(summary.get('avg_ctr', 0), 2),
                'cpc': round(summary.get('avg_cpc', 0), 2),
                'reach': summary.get('total_reach', 0)
            },
            'recent_trend': daily_trends[-3:] if len(daily_trends) >= 3 else daily_trends,
            'top_placements': top_placements
        }
        
        return optimized
    
    def ask_question(self, question: str, context: Dict[str, Any]) -> str:
        if not self.api_key:
            return "Xin lỗi, API key chưa được cấu hình. Vui lòng kiểm tra cài đặt."
        
        try:
            system_prompt = (
                "Bạn là chuyên gia phân tích Facebook Ads. Chỉ trả lời dựa trên dữ liệu được cung cấp, "
                "không suy diễn hoặc bịa thêm. Nếu dữ liệu không đủ, hãy nói 'chưa đủ dữ liệu'."
            )
            user_prompt = (
                "Ngữ cảnh dashboard (JSON):\n" + json.dumps(context or {}, ensure_ascii=False, indent=2) +
                "\n\nCâu hỏi: " + question +
                "\n\nYêu cầu: trả lời ngắn gọn, gạch đầu dòng rõ ràng, đề xuất hành động nếu phù hợp."
            )
            
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
    return render_template('index.html')

@app.route('/api/ads-data')
def get_ads_data():
    try:
        data = load_ads_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        context = data.get('context') or {}
        
        if not question:
            return jsonify({'error': 'Câu hỏi không được để trống'}), 400
        
        global_data = load_ads_data()
        if isinstance(context, dict):
            context.setdefault('extraction_date', global_data.get('extraction_date'))
            context.setdefault('campaigns_count', len(global_data.get('campaigns', [])))
        
        chatbot = OpenAIChatbot()
        
        answer = chatbot.ask_question(question, context)
        
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
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'openai_configured': bool(os.getenv('OPENAI_API_KEY'))
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    try:
        start_date = request.json.get('start_date') if request.is_json else None
        extractor = FacebookAdsExtractor()
        data = extractor.extract_all_data(start_date or "2023-01-01")
        ok = extractor.save_to_json(data, "ads_data.json")
        return jsonify({'ok': bool(ok), 'campaigns': len(data.get('campaigns', []))})
    except Exception as e:
        logger.error(f"Lỗi refresh: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/campaign-insights')
def api_campaign_insights():
    try:
        campaign_id = request.args.get('campaign_id', '').strip()
        since = request.args.get('since')
        until = request.args.get('until')
        date_preset = request.args.get('date_preset', '').strip()
        campaign_status = request.args.get('status', '').upper()
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

        initial_preset = 'last_7d' if campaign_status == 'ACTIVE' else 'last_30d'
        if date_preset:
            initial_preset = date_preset
        params = {
            'access_token': token,
            'fields': 'campaign_name,impressions,clicks,spend,ctr,cpc,cpm,reach,frequency,actions,inline_link_clicks,inline_link_click_ctr,unique_inline_link_clicks',
            'date_preset': initial_preset,
            'time_increment': 1
        }
        if since and until:
            params['date_preset'] = 'custom'
            params['since'] = since
            params['until'] = until

        status_code, data = fetch(params)
        if status_code != 200:
            err = data.get('error', {})
            if err.get('code') == 190:
                return jsonify({'error': err, 'token_expired': True, 'totals': {}, 'daily': []})
            params_f = {'access_token': token, 'fields': 'campaign_name,impressions,clicks,spend,ctr,cpc,cpm,reach,frequency', 'date_preset': 'lifetime'}
            st2, d2 = fetch(params_f)
            rows2 = d2.get('data', []) if st2 == 200 else []
            if rows2:
                return jsonify({'totals': {}, 'daily': rows2, 'note': 'Fallback to lifetime due to upstream error'})
            return jsonify({'error': err or {'message': 'Unknown error'}, 'totals': {}, 'daily': []})
        rows = data.get('data', [])

        if not rows:
            params2 = params.copy()
            if campaign_status == 'ACTIVE':
                params2['date_preset'] = 'last_30d'
            else:
                params2['date_preset'] = 'last_90d'
            status_code, data = fetch(params2)
            if status_code == 200:
                rows = data.get('data', [])

        if not rows and campaign_status == 'ACTIVE':
            for preset in ['yesterday', 'today']:
                params3a = params.copy()
                params3a['date_preset'] = preset
                sc_try, data = fetch(params3a)
                if sc_try == 200:
                    rows = data.get('data', [])
                    if rows:
                        break

        if not rows:
            params3 = {
                'access_token': token,
                'fields': 'campaign_name,impressions,clicks,spend,ctr,cpc,cpm,reach,frequency',
                'date_preset': 'lifetime'
            }
            status_code, data = fetch(params3)
            if status_code == 200:
                rows = data.get('data', [])
        def _row_date_key(r):
            return (r.get('date_start') or r.get('date') or r.get('date_stop') or '')
        try:
            rows = sorted(rows, key=_row_date_key)
        except Exception:
            pass

        totals = {
            'impressions': 0,
            'clicks': 0,
            'spend': 0.0,
            'reach': 0,
            'inline_link_clicks': 0,
            'post_engagement': 0,
            'photo_view': 0,
            'video_views': 0,
            'unique_inline_link_clicks': 0,
        }

        def sum_video_actions(action_list):
            if not isinstance(action_list, list):
                return 0
            total = 0
            for a in action_list:
                try:
                    total += int(float(a.get('value', 0) or 0))
                except Exception:
                    continue
            return total

        for r in rows:
            totals['impressions'] += int(float(r.get('impressions', 0) or 0))
            totals['clicks'] += int(float(r.get('clicks', 0) or 0))
            totals['spend'] += float(r.get('spend', 0) or 0)
            totals['reach'] += int(float(r.get('reach', 0) or 0))

            totals['inline_link_clicks'] += int(float(r.get('inline_link_clicks', 0) or 0))
            totals['unique_inline_link_clicks'] += int(float(r.get('unique_inline_link_clicks', 0) or 0))

            for a in (r.get('actions') or []):
                at = (a.get('action_type') or '').lower()
                try:
                    val = int(float(a.get('value', 0) or 0))
                except Exception:
                    val = 0
                if at == 'post_engagement':
                    totals['post_engagement'] += val
                elif at == 'photo_view':
                    totals['photo_view'] += val
                elif at in ('link_click', 'landing_page_view'):
                    totals['inline_link_clicks'] += val

            totals['video_views'] += sum_video_actions(r.get('video_play_actions'))
            totals['video_views'] += sum_video_actions(r.get('video_3_sec_watched_actions'))
            totals['video_views'] += sum_video_actions(r.get('video_10_sec_watched_actions'))

        totals['ctr'] = (totals['clicks'] / max(totals['impressions'], 1)) * 100.0
        totals['frequency'] = (totals['impressions'] / max(totals['reach'], 1)) if totals['reach'] > 0 else 0.0

        return jsonify({'totals': totals, 'daily': rows})
    except Exception as e:
        logger.error(f"Lỗi /api/campaign-insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign-breakdown')
def api_campaign_breakdown():
    try:
        campaign_id = request.args.get('campaign_id', '').strip()
        kind = request.args.get('kind', 'placement')
        date_preset = request.args.get('date_preset', 'last_30d')
        since = request.args.get('since')
        until = request.args.get('until')
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
            'fields': 'impressions,clicks,spend,ctr,cpc,cpm,reach,frequency,actions,inline_link_clicks,video_play_actions',
            'breakdowns': breakdowns,
            'date_preset': date_preset
        }
        if since and until:
            params['date_preset'] = 'custom'
            params['since'] = since
            params['until'] = until
        res = requests.get(f"{base_url}/{campaign_id}/insights", params=params, timeout=30)
        data = res.json()
        rows = []
        if res.status_code == 200:
            rows = data.get('data', [])
        else:
            if since and until:
                p2 = params.copy()
                p2.pop('since', None); p2.pop('until', None)
                p2['date_preset'] = 'last_30d'
                res_try = requests.get(f"{base_url}/{campaign_id}/insights", params=p2, timeout=30)
                if res_try.status_code == 200:
                    rows = res_try.json().get('data', [])
                    data = res_try.json()
                    res = res_try
            if not rows and kind == 'placement':
                fb_params = (p2 if (since and until) else params).copy()
                fb_params['breakdowns'] = 'publisher_platform,platform_position'
                res2 = requests.get(f"{base_url}/{campaign_id}/insights", params=fb_params, timeout=30)
                if res2.status_code == 200:
                    rows_raw = res2.json().get('data', [])
                    for r in rows_raw:
                        r['placement'] = f"{r.get('publisher_platform','')}:{r.get('platform_position','')}"
                    rows = rows_raw
                else:
                    err = data.get('error', {})
                    if err.get('code') == 190:
                        return jsonify({'error': err, 'token_expired': True, 'rows': []})
                    return jsonify({'error': err or {'message': 'Unknown error'}, 'rows': []})
            elif not rows:
                err = data.get('error', {})
                if err.get('code') == 190:
                    return jsonify({'error': err, 'token_expired': True, 'rows': []})
                return jsonify({'error': err or {'message': 'Unknown error'}, 'rows': []})
        return jsonify({'rows': rows})
    except Exception as e:
        logger.error(f"Lỗi /api/campaign-breakdown: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign-ads')
def api_campaign_ads():
    try:
        campaign_id = request.args.get('campaign_id', '').strip()
        date_preset = request.args.get('date_preset', 'last_30d')
        if not campaign_id:
            return jsonify({'error': 'campaign_id is required'}), 400
        token = get_access_token()
        base_url = 'https://graph.facebook.com/v23.0'

        ads_res = requests.get(f"{base_url}/{campaign_id}/ads", params={'access_token': token, 'fields': 'id,name,status,created_time', 'limit': 50}, timeout=30)
        ads_data = ads_res.json()
        if ads_res.status_code != 200:
            err = ads_data.get('error', {})
            if err.get('code') == 190:
                return jsonify({'error': err, 'token_expired': True, 'items': []})
            return jsonify({'error': err or {'message': 'Unknown error'}, 'items': []})
        ads = ads_data.get('data', [])

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

@app.route('/api/campaign-ai-insights', methods=['POST'])
def api_campaign_ai_insights():
    try:
        data = request.get_json()
        campaign_id = data.get('campaign_id', '').strip()
        
        if not campaign_id:
            return jsonify({'error': 'campaign_id is required'}), 400
        
        try:
            from flask import current_app
            with current_app.test_request_context(f'/api/campaign-insights?campaign_id={campaign_id}&status=ACTIVE'):
                insights_response_data = api_campaign_insights()
                if isinstance(insights_response_data, tuple):
                    insights_data = insights_response_data[0].get_json()
                else:
                    insights_data = insights_response_data.get_json()
                    
                if insights_data.get('error'):
                    return jsonify({'error': 'Không thể lấy dữ liệu insights: ' + str(insights_data.get('error'))}), 500
                    
        except Exception as e:
            logger.error(f"Lỗi khi lấy insights data: {e}")
            return jsonify({'error': 'Không thể lấy dữ liệu insights'}), 500
        
        try:
            with current_app.test_request_context(f'/api/campaign-breakdown?campaign_id={campaign_id}&kind=placement&date_preset=last_30d'):
                breakdown_response_data = api_campaign_breakdown()
                if isinstance(breakdown_response_data, tuple):
                    breakdown_data = breakdown_response_data[0].get_json()
                else:
                    breakdown_data = breakdown_response_data.get_json()
                    
                if breakdown_data.get('error'):
                    breakdown_data = {'rows': []}
                    
        except Exception as e:
            logger.error(f"Lỗi khi lấy breakdown data: {e}")
            breakdown_data = {'rows': []}
        
        campaign_analysis_data = {
            'campaign_id': campaign_id,
            'summary_metrics': {
                'total_impressions': insights_data.get('totals', {}).get('impressions', 0),
                'total_clicks': insights_data.get('totals', {}).get('clicks', 0),
                'total_spend': insights_data.get('totals', {}).get('spend', 0),
                'total_reach': insights_data.get('totals', {}).get('reach', 0),
                'avg_ctr': (insights_data.get('totals', {}).get('clicks', 0) / max(insights_data.get('totals', {}).get('impressions', 1), 1)) * 100,
                'avg_cpc': insights_data.get('totals', {}).get('spend', 0) / max(insights_data.get('totals', {}).get('clicks', 1), 1)
            },
            'daily_trends': insights_data.get('daily', [])[-7:],
            'placement_breakdown': breakdown_data.get('rows', [])[:10]
        }
        
        try:
            chatbot = OpenAIChatbot()
            ai_analysis = chatbot.analyze_campaign_performance(campaign_analysis_data)
            
            logger.info(f"AI analysis completed for campaign {campaign_id}, cached: {ai_analysis.get('cached', False)}")
            
            return jsonify({
                'success': True,
                'insights': ai_analysis['insights'],
                'recommendations': ai_analysis['recommendations'],
                'cached': ai_analysis.get('cached', False),
                'analysis_data': campaign_analysis_data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as ai_error:
            logger.error(f"AI analysis failed for campaign {campaign_id}: {ai_error}")
            return jsonify({
                'error': f'Lỗi phân tích AI: {str(ai_error)}'
            }), 500
        
    except Exception as e:
        logger.error(f"Lỗi /api/campaign-ai-insights: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Khởi động Flask app trên port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
