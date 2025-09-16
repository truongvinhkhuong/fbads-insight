#!/usr/bin/env python3
"""
Script chạy tất cả các tests cho Facebook Ads Dashboard
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

def run_command(command, description):
    """Chạy command và hiển thị kết quả"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("📤 Output:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Errors/Warnings:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - Thành công!")
        else:
            print(f"❌ {description} - Thất bại (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Lỗi khi chạy {description}: {e}")
        return False

def check_environment():
    """Kiểm tra môi trường"""
    print("🔧 Kiểm tra môi trường...")
    
    # Kiểm tra file .env
    if os.path.exists('.env'):
        print("✅ File .env tồn tại")
    else:
        print("❌ File .env không tồn tại")
        return False
    
    # Kiểm tra virtual environment
    if 'VIRTUAL_ENV' in os.environ:
        print(f"✅ Virtual environment: {os.environ['VIRTUAL_ENV']}")
    else:
        print("❌ Virtual environment chưa được kích hoạt")
        return False
    
    # Kiểm tra Python version
    python_version = sys.version_info
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    return True

def main():
    """Hàm chính"""
    print("🚀 Facebook Ads Dashboard - Test Suite")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Kiểm tra môi trường
    if not check_environment():
        print("\n❌ Môi trường không đủ điều kiện để chạy tests")
        sys.exit(1)
    
    print("\n✅ Môi trường đã sẵn sàng!")
    
    # Chạy các tests
    tests = [
        ("python test.py", "Unit Tests (unittest)"),
        ("python test_extractor.py", "Facebook Ads Extractor Test"),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for command, description in tests:
        if run_command(command, description):
            success_count += 1
    
    # Tóm tắt kết quả
    print(f"\n{'='*60}")
    print("📊 TÓM TẮT KẾT QUẢ TESTS")
    print(f"{'='*60}")
    print(f"✅ Tests thành công: {success_count}/{total_tests}")
    print(f"❌ Tests thất bại: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 Tất cả tests đã chạy thành công!")
        print("🚀 Ứng dụng đã sẵn sàng để sử dụng!")
    else:
        print(f"\n⚠️  Có {total_tests - success_count} test(s) thất bại")
        print("🔍 Vui lòng kiểm tra và sửa lỗi trước khi deploy")
    
    # Kiểm tra ứng dụng Flask
    print(f"\n{'='*60}")
    print("🌐 Kiểm tra ứng dụng Flask...")
    print(f"{'='*60}")
    
    try:
        import requests
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Flask app đang chạy trên port 5001")
            health_data = response.json()
            print(f"📊 Status: {health_data.get('status', 'Unknown')}")
            print(f"🔑 OpenAI configured: {health_data.get('openai_configured', False)}")
        else:
            print(f"❌ Flask app trả về status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối đến Flask app (port 5001)")
        print("💡 Có thể ứng dụng chưa được khởi động")
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra Flask app: {e}")
    
    print(f"\n{'='*60}")
    print("🏁 Test Suite hoàn thành!")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
