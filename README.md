
## Yêu cầu

- Python 3.9 trở lên
- Facebook Ads Access Token
- OpenAI API Key (tùy chọn, cho tính năng AI)

## Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd fb-ads
```

### 2. Tạo môi trường ảo
```bash
python3 -m venv env
source env/bin/activate  # macOS/Linux
# hoặc
env\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường
Tạo file `.env` với nội dung:
```
USER_TOKEN=your_facebook_access_token
FACEBOOK_ACCOUNT_IDS=act_123456789,act_987654321
OPENAI_API_KEY=your_openai_api_key
FLASK_SECRET_KEY=your_secret_key
SKIP_INSIGHTS=false
```

## Sử dụng

### 1. Trích xuất dữ liệu Facebook Ads
```bash
python facebook_ads_extractor.py
```
Script sẽ tạo file `ads_data.json` chứa dữ liệu chiến dịch quảng cáo.

### 2. Khởi động ứng dụng web
```bash
python app.py
```

Truy cập `http://localhost:5000` để xem dashboard.

## Cấu trúc dự án

```
fb-ads/
├── app.py                      # Ứng dụng Flask chính
├── facebook_ads_extractor.py   # Script trích xuất dữ liệu
├── requirements.txt            # Dependencies Python
├── Procfile                    # Cấu hình deploy Heroku
├── runtime.txt                 # Phiên bản Python
├── templates/
│   └── index.html             # Giao diện dashboard
├── static/                    # File CSS/JS tĩnh
└── ads_data.json              # Dữ liệu chiến dịch (tự tạo)
```

## API Endpoints

### GET /api/ads-data
Lấy dữ liệu tất cả chiến dịch quảng cáo.

### POST /api/ask
Gửi câu hỏi cho chatbot AI.
```json
{
  "question": "Chiến dịch nào có CTR cao nhất?",
  "context": {}
}
```

### GET /api/campaign-insights?campaign_id=123
Lấy insights chi tiết của một chiến dịch.

### GET /api/campaign-breakdown?campaign_id=123&kind=placement
Lấy phân tích theo placement/age/country.

### POST /api/campaign-ai-insights
Phân tích AI cho chiến dịch cụ thể.

### POST /api/refresh
Làm mới dữ liệu từ Facebook API.

## Deploy lên Heroku

### 1. Tạo ứng dụng Heroku
```bash
heroku create your-app-name
```

### 2. Cấu hình biến môi trường
```bash
heroku config:set USER_TOKEN=your_token
heroku config:set FACEBOOK_ACCOUNT_IDS=act_123456789
heroku config:set OPENAI_API_KEY=your_key
heroku config:set FLASK_SECRET_KEY=your_secret
```

### 3. Deploy
```bash
git push heroku main
```

## Deploy lên các nền tảng khác

### Render.com
- Build Command: `pip install -r requirements.txt`
- Start Command: `python app.py`
- Cấu hình biến môi trường trong dashboard

### Railway
- Kết nối GitHub repository
- Cấu hình biến môi trường
- Tự động deploy khi push code

## Xử lý lỗi thường gặp

### Token hết hạn
- Kiểm tra token Facebook trong file `.env`
- Tạo token mới từ Facebook Developer Console

### Thiếu quyền truy cập
- Đảm bảo token có quyền `ads_read`
- Kiểm tra Account ID có đúng không

### Lỗi OpenAI API
- Kiểm tra `OPENAI_API_KEY` trong file `.env`
- Đảm bảo có credit trong tài khoản OpenAI

## Phát triển

### Chạy tests
```bash
python test_extractor.py
python test_facebook_token.py
python test_page_token.py
```

### Debug mode
```bash
export FLASK_ENV=development
python app.py
```

