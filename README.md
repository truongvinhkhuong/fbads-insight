## Yêu cầu
- Python 3.9+
- Facebook Ads Access Token
- OpenAI API Key

## Cấu trúc
```
fb-ads/
├── app.py                      # Flask backend + HTML dashboard + chatbot
├── facebook_ads_extractor.py   # Script trích xuất dữ liệu -> ads_data.json
├── requirements.txt            # Dependencies tối thiểu
├── env_example.txt             # Mẫu biến môi trường (.env)
└── README.md                   # Hướng dẫn
```

## Cài đặt & chạy local
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp env_example.txt .env   # rồi sửa các biến thật
```

Trích xuất dữ liệu (tạo `ads_data.json`; tạo dữ liệu mẫu nếu token sai):
```bash
python facebook_ads_extractor.py
```

Chạy website:
```bash
python app.py
```
Mở `http://localhost:5000`.

## Deploy website (đơn giản)
- Render.com / Railway / Heroku / PythonAnywhere
  - Build: `pip install -r requirements.txt`
  - Start: `python app.py`
  - Env vars: `OPENAI_API_KEY`, `FACEBOOK_ACCESS_TOKEN`, `FACEBOOK_ACCOUNT_IDS`, `FLASK_SECRET_KEY`

Nếu nền tảng yêu cầu WSGI/PORT:
- Procfile (tùy chọn): `web: gunicorn app:app --bind 0.0.0.0:$PORT`
- Cài thêm: `pip install gunicorn`

## Lưu ý
- Không lưu API Key trong HTML; Flask gọi OpenAI API.
- Màu chủ đạo UI: #247ba0.
- Dashboard đọc `ads_data.json`; nếu chưa có dữ liệu thực, extractor tự tạo dữ liệu mẫu.
