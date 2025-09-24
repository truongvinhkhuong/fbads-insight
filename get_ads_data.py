#!/usr/bin/env python3

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, date

def get_ads_data():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    account_id = os.getenv('FACEBOOK_ACCOUNT_IDS', '').split(',')[0].strip()
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    print(f"Account ID: {account_id}")
    
    try:
        url = f"{base_url}/{account_id}/ads"
        params = {
            'access_token': access_token,
            'fields': 'id,name,status,created_time,updated_time,effective_status,campaign_id,adset_id',
            'limit': 100
        }
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if 'error' in data:
            print(f"Lỗi API: {data['error']}")
            return
        
        ads = data.get('data', [])
        print(f"Tìm thấy {len(ads)} quảng cáo:")
        
        if ads:
            for i, ad in enumerate(ads[:10]):
                print(f"\n{i+1}. {ad.get('name', 'N/A')} (ID: {ad.get('id')})")
                print(f"   - Trạng thái: {ad.get('status')}")
                print(f"   - Trạng thái hiệu quả: {ad.get('effective_status')}")
                print(f"   - Tạo lúc: {ad.get('created_time')}")
                print(f"   - Cập nhật: {ad.get('updated_time')}")
                print(f"   - Campaign ID: {ad.get('campaign_id')}")
                print(f"   - AdSet ID: {ad.get('adset_id')}")
        else:
            print("Không có quảng cáo nào")
            return
        
        for i, ad in enumerate(ads[:5]):
            ad_id = ad.get('id')
            ad_name = ad.get('name', 'N/A')
            
            print(f"\n{i+1}. Lấy insights cho: {ad_name}")
            
            try:
                url = f"{base_url}/{ad_id}/insights"
                params = {
                    'access_token': access_token,
                    'fields': 'impressions,clicks,spend,ctr,cpc,cpm,reach,frequency,actions',
                    'date_preset': 'lifetime'
                }
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    insights = data.get('data', [])
                    
                    if insights:
                        insight = insights[0]
                        print(f"   Insights:")
                        print(f"      - Impressions: {insight.get('impressions', 'N/A')}")
                        print(f"      - Clicks: {insight.get('clicks', 'N/A')}")
                        print(f"      - Spend: {insight.get('spend', 'N/A')}")
                        print(f"      - CTR: {insight.get('ctr', 'N/A')}")
                        print(f"      - CPC: {insight.get('cpc', 'N/A')}")
                        print(f"      - CPM: {insight.get('cpm', 'N/A')}")
                        print(f"      - Reach: {insight.get('reach', 'N/A')}")
                    else:
                        print(f"   Không có insights")
                else:
                    print(f"   Lỗi: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"   Lỗi: {e}")
        
        all_data = {
            'extraction_date': datetime.now().isoformat(),
            'start_date': '2023-01-01',
            'ads': []
        }
        
        for ad in ads:
            ad_data = {
                'account_id': account_id,
                'ad_id': ad.get('id'),
                'ad_name': ad.get('name', 'Unknown'),
                'status': ad.get('status', 'Unknown'),
                'effective_status': ad.get('effective_status', 'Unknown'),
                'created_time': ad.get('created_time', ''),
                'updated_time': ad.get('updated_time', ''),
                'campaign_id': ad.get('campaign_id', ''),
                'adset_id': ad.get('adset_id', ''),
                'insights': {}
            }
            
            try:
                url = f"{base_url}/{ad.get('id')}/insights"
                params = {
                    'access_token': access_token,
                    'fields': 'impressions,clicks,spend,ctr,cpc,cpm,reach,frequency',
                    'date_preset': 'lifetime'
                }
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    insights = data.get('data', [])
                    if insights:
                        ad_data['insights'] = insights[0]
            except:
                pass
            
            all_data['ads'].append(ad_data)
        
        # Lưu dữ liệu
        with open('ads_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"Đã lưu {len(all_data['ads'])} quảng cáo vào ads_data.json")
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    get_ads_data()
