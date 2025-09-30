#!/usr/bin/env python3

import requests
import json

def test_meta_report_api():
    """Test Meta Report Insights API endpoint"""
    try:
        # Test the API endpoint
        url = "http://localhost:5002/api/meta-report-insights"
        params = {"date_preset": "last_30d"}
        
        print(f"Testing API: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response successful!")
            print(f"Keys in response: {list(data.keys())}")
            
            if 'monthly_data' in data:
                print(f"Monthly data count: {len(data['monthly_data'])}")
                if data['monthly_data']:
                    print(f"First month data: {data['monthly_data'][0]}")
            
            if 'brand_analysis' in data:
                print(f"Brand analysis count: {len(data['brand_analysis'])}")
                if data['brand_analysis']:
                    print(f"First brand: {list(data['brand_analysis'].keys())[0]}")
            
            if 'content_analysis' in data:
                print(f"Content analysis count: {len(data['content_analysis'])}")
                if data['content_analysis']:
                    print(f"First content format: {list(data['content_analysis'].keys())[0]}")
                    
        else:
            print("❌ API Response failed!")
            try:
                error_data = response.json()
                print(f"Error data: {error_data}")
            except:
                print(f"Error text: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on port 5002")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_meta_report_api()
