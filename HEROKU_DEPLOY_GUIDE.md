# 🚀 Hướng dẫn Deploy lên Heroku

## Bước 1: Cài đặt Heroku CLI

### Trên macOS (với Homebrew):
```bash
brew install heroku/brew/heroku
```

### Hoặc tải trực tiếp:
- Truy cập: https://devcenter.heroku.com/articles/heroku-cli
- Tải và cài đặt theo hướng dẫn

## Bước 2: Đăng nhập Heroku
```bash
heroku login
```

## Bước 3: Deploy tự động
Chạy script deploy đã tạo:
```bash
./deploy_to_heroku.sh
```

## Bước 4: Deploy thủ công (nếu cần)

### Tạo app Heroku:
```bash
heroku create your-app-name
```

### Cấu hình environment variables:
```bash
# Cấu hình từ file .env
heroku config:set USER_TOKEN="your_facebook_token" --app your-app-name
heroku config:set OPENAI_API_KEY="your_openai_key" --app your-app-name
heroku config:set FACEBOOK_ACCESS_TOKEN="your_facebook_token" --app your-app-name
heroku config:set FLASK_SECRET_KEY="your_secret_key" --app your-app-name
heroku config:set HEROKU_API_KEY="your_heroku_api_key" --app your-app-name

# Cấu hình môi trường
heroku config:set FLASK_ENV=production --app your-app-name
```

### Deploy code:
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Mở ứng dụng:
```bash
heroku open --app your-app-name
```

## Bước 5: Kiểm tra và Debug

### Xem logs:
```bash
heroku logs --tail --app your-app-name
```

### Kiểm tra status:
```bash
heroku ps --app your-app-name
```

### Kiểm tra config:
```bash
heroku config --app your-app-name
```

## Cấu trúc file đã tạo cho Heroku:

- ✅ `Procfile` - Định nghĩa cách chạy app
- ✅ `runtime.txt` - Chỉ định Python version
- ✅ `requirements.txt` - Dependencies (đã thêm gunicorn)
- ✅ `deploy_to_heroku.sh` - Script deploy tự động

## Lưu ý quan trọng:

1. **Environment Variables**: Đảm bảo tất cả biến môi trường trong `.env` đã được set trên Heroku
2. **Port**: Ứng dụng đã được cấu hình để sử dụng `PORT` từ Heroku
3. **Debug**: Trong production, debug mode sẽ tự động tắt
4. **Logs**: Sử dụng `heroku logs --tail` để theo dõi lỗi

## Troubleshooting:

### Lỗi "No web processes running":
```bash
heroku ps:scale web=1 --app your-app-name
```

### Lỗi "App crashed":
```bash
heroku logs --tail --app your-app-name
```

### Lỗi "Build failed":
```bash
heroku logs --build --app your-app-name
```

## Cập nhật ứng dụng:
```bash
git add .
git commit -m "Update app"
git push heroku main
```
