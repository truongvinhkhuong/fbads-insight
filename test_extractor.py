#!/usr/bin/env python3
"""
Test đơn giản cho Facebook Ads Extractor
"""

import os
from dotenv import load_dotenv
from facebook_ads_extractor import FacebookAdsExtractor

def test_extractor():
    """Test Facebook Ads Extractor"""
    print("🧪 Testing Facebook Ads Extractor...")
    
    try:
        # Khởi tạo extractor
        extractor = FacebookAdsExtractor()
        print("✅ Extractor khởi tạo thành công")
        
        # Test kết nối
        print("🔗 Testing kết nối Facebook API...")
        connection_result = extractor.test_connection()
        
        if connection_result:
            print("✅ Kết nối Facebook API thành công!")
            
            # Test lấy campaigns
            if extractor.account_ids:
                account_id = extractor.account_ids[0].strip()
                print(f"📊 Lấy campaigns từ tài khoản: {account_id}")
                
                campaigns = extractor.get_campaigns(account_id)
                print(f"📈 Tìm thấy {len(campaigns)} campaigns")
                
                if campaigns:
                    print("📋 Danh sách campaigns:")
                    for i, campaign in enumerate(campaigns[:5], 1):  # Chỉ hiển thị 5 campaigns đầu
                        print(f"  {i}. {campaign.get('name', 'Unknown')} - {campaign.get('status', 'Unknown')}")
        else:
            print("❌ Kết nối Facebook API thất bại")
            print("💡 Có thể do:")
            print("   - Access token đã hết hạn")
            print("   - Không có quyền truy cập")
            print("   - Tài khoản quảng cáo không hợp lệ")
    
    except ValueError as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        print("💡 Kiểm tra file .env và các biến môi trường")
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")
    
    required_vars = [
        'FACEBOOK_ACCESS_TOKEN',
        'FACEBOOK_ACCOUNT_IDS',
        'OPENAI_API_KEY',
        'FLASK_SECRET_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'FACEBOOK_ACCESS_TOKEN':
                # Chỉ hiển thị 10 ký tự đầu và cuối của token
                masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
                print(f"✅ {var}: {masked_value}")
            elif var == 'FACEBOOK_ACCOUNT_IDS':
                print(f"✅ {var}: {value}")
            else:
                print(f"✅ {var}: {'***' if 'KEY' in var or 'SECRET' in var else value}")
        else:
            print(f"❌ {var}: Không được cấu hình")

if __name__ == '__main__':
    load_dotenv()
    
    print("🚀 Facebook Ads Extractor Test")
    print("=" * 50)
    
    test_environment()
    print()
    test_extractor()
    
    print("\n" + "=" * 50)
    print("🏁 Test hoàn thành!")
