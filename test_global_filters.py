#!/usr/bin/env python3
"""
Test script for Global Filters functionality
"""

import requests
import json
import sys
from datetime import datetime, timedelta

def test_api_endpoints():
    """Test the new API endpoints for global filters"""
    base_url = "http://localhost:5002"
    
    print("🧪 Testing Global Filters API Endpoints...")
    print("=" * 50)
    
    # Test 1: Filter Options API
    print("\n1. Testing /api/filter-options")
    try:
        response = requests.get(f"{base_url}/api/filter-options", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('brands', []))} brands")
            print(f"   - Brands: {data.get('brands', [])}")
            print(f"   - Campaigns: {len(data.get('campaigns', []))}")
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Filtered Data API with different parameters
    print("\n2. Testing /api/filtered-data")
    test_params = [
        {"date_preset": "last_7d"},
        {"date_preset": "last_30d"},
        {"date_preset": "custom", "since": "2024-01-01", "until": "2024-01-31"},
    ]
    
    for i, params in enumerate(test_params, 1):
        try:
            response = requests.get(f"{base_url}/api/filtered-data", params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                totals = data.get('totals', {})
                print(f"✅ Test {i}: {params}")
                print(f"   - Impressions: {totals.get('impressions', 0):,}")
                print(f"   - Clicks: {totals.get('clicks', 0):,}")
                print(f"   - Spend: ${totals.get('spend', 0):.2f}")
                print(f"   - Filtered campaigns: {data.get('filtered_campaigns', 0)}")
            else:
                print(f"❌ Test {i} Error: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Test {i} Exception: {e}")
    
    # Test 3: Existing endpoints with new filter parameters
    print("\n3. Testing existing endpoints with filter parameters")
    existing_endpoints = [
        "/api/daily-tracking",
        "/api/meta-report-insights",
    ]
    
    for endpoint in existing_endpoints:
        try:
            params = {"date_preset": "last_7d", "brand": "BBI"}
            response = requests.get(f"{base_url}{endpoint}", params=params, timeout=15)
            if response.status_code == 200:
                print(f"✅ {endpoint}: Success with filter params")
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Exception {e}")

def test_frontend_integration():
    """Test frontend integration"""
    print("\n🎨 Testing Frontend Integration...")
    print("=" * 50)
    
    # Check if the main page loads
    try:
        response = requests.get("http://localhost:5002/", timeout=10)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            
            # Check if global filters component is included
            if "global-filters" in response.text:
                print("✅ Global filters component found in HTML")
            else:
                print("❌ Global filters component not found in HTML")
            
            # Check if global-filters.js is included
            if "global-filters.js" in response.text:
                print("✅ Global filters JavaScript file found")
            else:
                print("❌ Global filters JavaScript file not found")
                
        else:
            print(f"❌ Main page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend test exception: {e}")

def test_filter_logic():
    """Test filter logic with sample data"""
    print("\n🔍 Testing Filter Logic...")
    print("=" * 50)
    
    # Sample campaign data
    sample_campaigns = [
        {"campaign_id": "123", "campaign_name": "BBI Video Campaign", "status": "ACTIVE"},
        {"campaign_id": "456", "campaign_name": "Meta Image Campaign", "status": "PAUSED"},
        {"campaign_id": "789", "campaign_name": "Google Text Campaign", "status": "ACTIVE"},
    ]
    
    # Test brand extraction
    from app import extract_brand_from_campaign_name
    
    print("Testing brand extraction:")
    for campaign in sample_campaigns:
        brand = extract_brand_from_campaign_name(campaign["campaign_name"])
        print(f"   - {campaign['campaign_name']} → {brand}")
    
    # Test filtering
    print("\nTesting brand filtering:")
    bbi_campaigns = [c for c in sample_campaigns if extract_brand_from_campaign_name(c["campaign_name"]) == "BBI"]
    print(f"   - BBI campaigns: {len(bbi_campaigns)}")
    
    active_campaigns = [c for c in sample_campaigns if c["status"] == "ACTIVE"]
    print(f"   - Active campaigns: {len(active_campaigns)}")

def main():
    """Main test function"""
    print("🚀 Global Filters Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5002/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start the Flask app first.")
            print("   Run: python app.py")
            return
    except:
        print("❌ Server not responding. Please start the Flask app first.")
        print("   Run: python app.py")
        return
    
    print("✅ Server is running")
    
    # Run tests
    test_filter_logic()
    test_api_endpoints()
    test_frontend_integration()
    
    print("\n" + "=" * 60)
    print("🏁 Test Suite Completed")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

