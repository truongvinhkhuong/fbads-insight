#!/usr/bin/env python3
"""
Facebook Ads Data Extractor using PyAirbyte
Trích xuất dữ liệu quảng cáo từ Facebook Marketing API
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookAdsExtractor:
    """Class để trích xuất dữ liệu từ Facebook Ads API"""
    
    def __init__(self):
        load_dotenv()
        # Ưu tiên USER_TOKEN nếu có, sau đó fallback về FACEBOOK_ACCESS_TOKEN
        self.access_token = os.getenv('USER_TOKEN') or os.getenv('FACEBOOK_ACCESS_TOKEN')
        # Cho phép bỏ qua việc lấy insights qua biến môi trường
        self.skip_insights = (os.getenv('SKIP_INSIGHTS', 'true').lower() in ['1', 'true', 'yes'])
        self.account_ids = os.getenv('FACEBOOK_ACCOUNT_IDS', '').split(',')
        self.base_url = "https://graph.facebook.com/v23.0"
        self._page_cache = {}
        
        if not self.access_token:
            raise ValueError("USER_TOKEN hoặc FACEBOOK_ACCESS_TOKEN không được cấu hình")
        if not self.account_ids or self.account_ids[0] == '':
            raise ValueError("FACEBOOK_ACCOUNT_IDS không được cấu hình")

    def _infer_campaign_page(self, campaign_id: str) -> Dict[str, str]:
        """Suy luận page_id/page_name từ creatives của ads trong campaign (best-effort)"""
        try:
            # Lấy 1-3 ads để giảm số request
            ads_res = requests.get(
                f"{self.base_url}/{campaign_id}/ads",
                params={
                    'access_token': self.access_token,
                    'fields': 'id,adcreatives{object_story_id,object_id,instagram_actor_id}',
                    'limit': 3
                }
            )
            if ads_res.status_code != 200:
                return {}
            ads = ads_res.json().get('data', [])
            page_id = None
            for ad in ads:
                creatives = (ad.get('adcreatives') or {}).get('data') or []
                for cr in creatives:
                    osid = cr.get('object_story_id') or ''  # dạng "<pageid>_<postid>"
                    if '_' in osid:
                        page_id = osid.split('_')[0]
                        break
                if page_id:
                    break
            if not page_id:
                return {}
            # Lấy page name (có cache)
            if page_id in self._page_cache:
                return {'page_id': page_id, 'page_name': self._page_cache[page_id]}
            page_res = requests.get(f"{self.base_url}/{page_id}", params={'access_token': self.access_token, 'fields': 'name'})
            if page_res.status_code == 200:
                name = page_res.json().get('name') or ''
                self._page_cache[page_id] = name
                return {'page_id': page_id, 'page_name': name}
            return {'page_id': page_id, 'page_name': ''}
        except Exception:
            return {}
    
    def test_connection(self) -> bool:
        """Kiểm tra kết nối đến Facebook API"""
        try:
            url = f"{self.base_url}/me/adaccounts"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Kết nối thành công! Tìm thấy {len(data.get('data', []))} tài khoản quảng cáo")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi kết nối: {e}")
            return False
    
    def get_campaigns(self, account_id: str) -> List[Dict[str, Any]]:
        """Lấy danh sách các chiến dịch quảng cáo"""
        try:
            url = f"{self.base_url}/{account_id}/campaigns"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,status,objective,created_time,start_time,stop_time',
                'limit': 100
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            campaigns = data.get('data', [])
            
            # Kiểm tra nếu có lỗi trong response
            if 'error' in data:
                logger.warning(f"Lỗi API khi lấy campaigns: {data['error']}")
                return []
            
            logger.info(f"Lấy được {len(campaigns)} chiến dịch từ tài khoản {account_id}")
            
            # Nếu không có campaigns, kiểm tra quyền truy cập
            if len(campaigns) == 0:
                logger.info("Không tìm thấy chiến dịch nào. Có thể tài khoản chưa có chiến dịch hoặc thiếu quyền truy cập.")
                
                # Kiểm tra quyền ads_read
                try:
                    perm_url = f"{self.base_url}/me/permissions"
                    perm_response = requests.get(perm_url, params={'access_token': self.access_token})
                    if perm_response.status_code == 200:
                        permissions = perm_response.json().get('data', [])
                        ads_read_granted = any(p.get('permission') == 'ads_read' and p.get('status') == 'granted' for p in permissions)
                        if not ads_read_granted:
                            logger.warning("Thiếu quyền 'ads_read'. Cần cấp quyền này để đọc dữ liệu quảng cáo.")
                except:
                    pass
            
            return campaigns
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi lấy chiến dịch: {e}")
            return []
    
    def get_campaign_insights(self, account_id: str, campaign_id: str, start_date: str = "2023-01-01") -> Dict[str, Any]:
        """Lấy thông tin insights của chiến dịch"""
        try:
            # Gọi trực tiếp insights trên campaign để tránh lỗi tham số
            url = f"{self.base_url}/{campaign_id}/insights"
            params = {
                'access_token': self.access_token,
                'level': 'campaign',
                'fields': 'campaign_name,impressions,clicks,spend,ctr,cpc,cpm,reach,frequency,actions,inline_link_clicks,inline_link_click_ctr,unique_inline_link_clicks,video_play_actions,video_3_sec_watched_actions,video_10_sec_watched_actions,video_p25_watched_actions,video_p50_watched_actions,video_p75_watched_actions,video_p95_watched_actions,video_avg_time_watched_actions',
                'date_preset': 'custom',
                'since': start_date,
                'until': date.today().isoformat(),
                'time_increment': 1
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            insights = response.json().get('data', [])
            if insights:
                return insights[0]
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi lấy insights: {e}")
            return {}
    
    def extract_all_data(self, start_date: str = "2023-01-01") -> Dict[str, Any]:
        """Trích xuất tất cả dữ liệu quảng cáo"""
        all_data = {
            'extraction_date': datetime.now().isoformat(),
            'start_date': start_date,
            'campaigns': []
        }
        
        for account_id in self.account_ids:
            account_id = account_id.strip()
            if not account_id:
                continue
                
            logger.info(f"Đang xử lý tài khoản: {account_id}")
            
            # Lấy danh sách chiến dịch
            campaigns = self.get_campaigns(account_id)
            
            for campaign in campaigns:
                campaign_data = {
                    'account_id': account_id,
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign.get('name', 'Unknown'),
                    'status': campaign.get('status', 'Unknown'),
                    'objective': campaign.get('objective', 'Unknown'),
                    'created_time': campaign.get('created_time', ''),
                    'start_time': campaign.get('start_time', ''),
                    'stop_time': campaign.get('stop_time', ''),
                    'insights': {}
                }
                # Gắn thông tin Page nếu suy luận được
                page_info = self._infer_campaign_page(campaign['id'])
                if page_info:
                    campaign_data.update(page_info)
                
                # Lấy insights nếu không skip và chiến dịch đang hoạt động
                if not self.skip_insights and campaign.get('status') == 'ACTIVE':
                    insights = self.get_campaign_insights(account_id, campaign['id'], start_date)
                    campaign_data['insights'] = insights
                
                all_data['campaigns'].append(campaign_data)
        
        return all_data
    
    def save_to_json(self, data: Dict[str, Any], filename: str = "ads_data.json") -> bool:
        """Lưu dữ liệu vào file JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dữ liệu đã được lưu vào {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu file: {e}")
            return False
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """Tạo dữ liệu mẫu để test dashboard"""
        sample_data = {
            'extraction_date': datetime.now().isoformat(),
            'start_date': '2023-01-01',
            'campaigns': [
                {
                    'account_id': 'act_123456789',
                    'campaign_id': '123456789',
                    'campaign_name': 'Campaign A - Brand Awareness',
                    'status': 'ACTIVE',
                    'objective': 'BRAND_AWARENESS',
                    'created_time': '2023-01-15T00:00:00+0000',
                    'start_time': '2023-01-15T00:00:00+0000',
                    'stop_time': None,
                    'insights': {
                        'campaign_name': 'Campaign A - Brand Awareness',
                        'impressions': '150000',
                        'clicks': '2500',
                        'spend': '5000.00',
                        'ctr': '1.67',
                        'cpc': '2.00',
                        'cpm': '33.33'
                    }
                },
                {
                    'account_id': 'act_123456789',
                    'campaign_id': '123456790',
                    'campaign_name': 'Campaign B - Conversions',
                    'status': 'ACTIVE',
                    'objective': 'CONVERSIONS',
                    'created_time': '2023-02-01T00:00:00+0000',
                    'start_time': '2023-02-01T00:00:00+0000',
                    'stop_time': None,
                    'insights': {
                        'campaign_name': 'Campaign B - Conversions',
                        'impressions': '80000',
                        'clicks': '4000',
                        'spend': '8000.00',
                        'ctr': '5.00',
                        'cpc': '2.00',
                        'cpm': '100.00'
                    }
                },
                {
                    'account_id': 'act_123456789',
                    'campaign_id': '123456791',
                    'campaign_name': 'Campaign C - Traffic',
                    'status': 'ACTIVE',
                    'objective': 'TRAFFIC',
                    'created_time': '2023-03-01T00:00:00+0000',
                    'start_time': '2023-03-01T00:00:00+0000',
                    'stop_time': None,
                    'insights': {
                        'campaign_name': 'Campaign C - Traffic',
                        'impressions': '120000',
                        'clicks': '3000',
                        'spend': '6000.00',
                        'ctr': '2.50',
                        'cpc': '2.00',
                        'cpm': '50.00'
                    }
                }
            ]
        }
        
        return sample_data

def main():
    """Hàm chính để chạy trích xuất dữ liệu"""
    try:
        # Khởi tạo extractor
        extractor = FacebookAdsExtractor()
        
        # Kiểm tra kết nối
        if not extractor.test_connection():
            logger.warning("Không thể kết nối đến Facebook API. Tạo dữ liệu mẫu...")
            sample_data = extractor.generate_sample_data()
            extractor.save_to_json(sample_data, "ads_data.json")
            return
        
        # Trích xuất dữ liệu thực
        logger.info("Bắt đầu trích xuất dữ liệu...")
        data = extractor.extract_all_data("2023-01-01")
        
        # Kiểm tra nếu không có dữ liệu thực
        if not data.get('campaigns') or len(data['campaigns']) == 0:
            logger.warning("Không tìm thấy chiến dịch nào trong tài khoản quảng cáo.")
            logger.info("Có thể do:")
            logger.info("1. Tài khoản chưa có chiến dịch quảng cáo nào")
            logger.info("2. Thiếu quyền 'ads_read' (cần cấp quyền này)")
            logger.info("3. Chiến dịch đã bị xóa hoặc ẩn")
            logger.info("Tạo dữ liệu mẫu để demo dashboard...")
            
            sample_data = extractor.generate_sample_data()
            if extractor.save_to_json(sample_data, "ads_data.json"):
                logger.info("Đã tạo dữ liệu mẫu thành công!")
            else:
                logger.error("Lỗi khi tạo dữ liệu mẫu!")
        else:
            # Lưu dữ liệu thực
            if extractor.save_to_json(data, "ads_data.json"):
                logger.info("Trích xuất dữ liệu hoàn tất thành công!")
            else:
                logger.error("Lỗi khi lưu dữ liệu!")
            
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()
