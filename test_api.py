#!/usr/bin/env python3
"""
Test script để kiểm tra các API endpoints
"""

import requests
import json
from datetime import datetime, timedelta

def test_api_endpoints():
    base_url = "http://localhost:5002"
    
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    # Test 1: Basic API test
    print("\n1. Testing /api/test endpoint...")
    try:
        response = requests.get(f"{base_url}/api/test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {data}")
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Page insights API (without credentials)
    print("\n2. Testing /api/page-insights endpoint...")
    try:
        response = requests.get(f"{base_url}/api/page-insights")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got page insights data")
            print(f"   - Page name: {data.get('page_info', {}).get('name', 'N/A')}")
            print(f"   - Fan count: {data.get('page_info', {}).get('fan_count', 0)}")
            print(f"   - Total impressions: {data.get('summary_metrics', {}).get('total_impressions', 0)}")
        elif response.status_code == 400:
            data = response.json()
            print(f"⚠️  EXPECTED ERROR: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ UNEXPECTED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Page posts insights API
    print("\n3. Testing /api/page-posts-insights endpoint...")
    try:
        response = requests.get(f"{base_url}/api/page-posts-insights")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got posts insights data")
            print(f"   - Total posts: {data.get('total_posts', 0)}")
            print(f"   - Content types: {data.get('content_types', {})}")
        elif response.status_code == 400:
            data = response.json()
            print(f"⚠️  EXPECTED ERROR: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ UNEXPECTED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 4: Demo API endpoint
    print("\n4. Testing /api/page-insights-demo endpoint...")
    try:
        response = requests.get(f"{base_url}/api/page-insights-demo")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got demo data")
            print(f"   - Page name: {data.get('page_info', {}).get('name', 'N/A')}")
            print(f"   - Fan count: {data.get('page_info', {}).get('fan_count', 0)}")
            print(f"   - Total impressions: {data.get('summary_metrics', {}).get('total_impressions', 0)}")
            print(f"   - Daily data points: {len(data.get('daily_data', []))}")
            print(f"   - Top posts: {len(data.get('top_posts', []))}")
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 5: Test with date filters (real API)
    print("\n5. Testing real API with date filters...")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'since': start_date.strftime('%Y-%m-%d'),
            'until': end_date.strftime('%Y-%m-%d'),
            'post_type': 'photo'
        }
        
        response = requests.get(f"{base_url}/api/page-insights", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got filtered data")
            print(f"   - Date range: {data.get('date_range', {})}")
            print(f"   - Filter applied: {data.get('filter_applied', {})}")
        elif response.status_code == 400:
            data = response.json()
            print(f"⚠️  EXPECTED ERROR: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ UNEXPECTED: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 API Testing Complete!")

if __name__ == "__main__":
    test_api_endpoints()
