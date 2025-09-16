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
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.account_ids = os.getenv('FACEBOOK_ACCOUNT_IDS', '').split(',')
        self.base_url = "https://graph.facebook.com/v23.0"
        
        if not self.access_token:
            raise ValueError("FACEBOOK_ACCESS_TOKEN không được cấu hình")
        if not self.account_ids or self.account_ids[0] == '':
            raise ValueError("FACEBOOK_ACCOUNT_IDS không được cấu hình")
    
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
            
            campaigns = response.json().get('data', [])
            logger.info(f"Lấy được {len(campaigns)} chiến dịch từ tài khoản {account_id}")
            return campaigns
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi lấy chiến dịch: {e}")
            return []
    
    def get_campaign_insights(self, account_id: str, campaign_id: str, start_date: str = "2023-01-01") -> Dict[str, Any]:
        """Lấy thông tin insights của chiến dịch"""
        try:
            url = f"{self.base_url}/{account_id}/insights"
            params = {
                'access_token': self.access_token,
                'level': 'campaign',
                'campaign_id': campaign_id,
                'fields': 'campaign_name,impressions,clicks,spend,ctr,cpc,cpm',
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
                
                # Lấy insights nếu chiến dịch đang hoạt động
                if campaign.get('status') == 'ACTIVE':
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
        
        # Lưu dữ liệu
        if extractor.save_to_json(data, "ads_data.json"):
            logger.info("Trích xuất dữ liệu hoàn tất thành công!")
        else:
            logger.error("Lỗi khi lưu dữ liệu!")
            
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()
