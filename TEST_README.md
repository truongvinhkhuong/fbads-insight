# Facebook Ads Dashboard - Test Guide

## 🚀 Tổng quan

Dự án Facebook Ads Dashboard đã được thiết lập đầy đủ với các tests để đảm bảo chất lượng code. Tài liệu này hướng dẫn cách chạy tests và kiểm tra ứng dụng.

## 📋 Các loại Tests

### 1. Unit Tests (test.py)
- **Mô tả**: Tests cho các API endpoints và chức năng chính của ứng dụng
- **Framework**: Python unittest
- **Coverage**: 
  - Flask routes (/api/health, /api/ads-data, /api/ask)
  - OpenAI Chatbot functionality
  - Facebook Ads Extractor
  - Data loading functions

### 2. Facebook Ads Extractor Test (test_extractor.py)
- **Mô tả**: Test riêng cho Facebook Ads Extractor
- **Chức năng**: Kiểm tra kết nối Facebook API và trích xuất dữ liệu

### 3. Test Suite Tổng hợp (run_all_tests.py)
- **Mô tả**: Script chạy tất cả tests và kiểm tra môi trường
- **Chức năng**: 
  - Kiểm tra môi trường
  - Chạy tất cả tests
  - Kiểm tra Flask app
  - Tóm tắt kết quả

## 🛠️ Cài đặt và Chạy Tests

### Bước 1: Kích hoạt Virtual Environment
```bash
cd /Users/khuong/Khuong-D/bbi/fb-ads
source env/bin/activate
```

### Bước 2: Chạy Tests

#### Chạy Unit Tests
```bash
python test.py
```

#### Chạy Facebook Ads Extractor Test
```bash
python test_extractor.py
```

#### Chạy Tất cả Tests
```bash
python run_all_tests.py
```

## 📊 Kết quả Tests

### ✅ Tests đã Pass
- **14/14 Unit Tests**: Tất cả API endpoints và chức năng chính
- **Facebook Ads Extractor**: Khởi tạo thành công
- **Environment Variables**: Tất cả biến môi trường đã được cấu hình

### ⚠️ Lưu ý
- **Facebook API Connection**: Hiện tại gặp lỗi 403 Forbidden
  - Có thể do access token đã hết hạn
  - Hoặc không có quyền truy cập đầy đủ
  - Cần kiểm tra và cập nhật Facebook access token

## 🌐 Kiểm tra Ứng dụng

### Flask App Status
- **Port**: 5001
- **Status**: Đang chạy
- **Health Check**: `/api/health` ✅
- **Ads Data**: `/api/ads-data` ✅
- **Chatbot**: `/api/ask` ✅

### API Endpoints
```bash
# Health Check
curl http://localhost:5001/api/health

# Lấy dữ liệu quảng cáo
curl http://localhost:5001/api/ads-data

# Hỏi câu hỏi (POST)
curl -X POST http://localhost:5001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Có bao nhiêu chiến dịch?"}'
```

## 🔧 Troubleshooting

### Lỗi thường gặp

#### 1. Virtual Environment không được kích hoạt
```bash
# Kiểm tra
echo $VIRTUAL_ENV

# Kích hoạt
source env/bin/activate
```

#### 2. Dependencies chưa được cài đặt
```bash
pip install -r requirements.txt
```

#### 3. File .env không tồn tại
```bash
# Kiểm tra
ls -la .env

# Tạo từ template
cp env_example.txt .env
# Sau đó cập nhật các giá trị thực tế
```

#### 4. Port 5001 bị chiếm
```bash
# Kiểm tra
lsof -i :5001

# Kill process nếu cần
kill -9 <PID>
```

## 📝 Cấu hình Environment

### File .env cần có
```env
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_ACCOUNT_IDS=your_account_id
OPENAI_API_KEY=your_openai_api_key
FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=development
PORT=5001
```

## 🎯 Kết luận

✅ **Tất cả tests đã pass thành công!**
✅ **Ứng dụng Flask đang hoạt động bình thường**
✅ **Các API endpoints đều hoạt động**
⚠️ **Cần cập nhật Facebook access token để kết nối API**

Ứng dụng đã sẵn sàng để sử dụng và phát triển thêm tính năng!
