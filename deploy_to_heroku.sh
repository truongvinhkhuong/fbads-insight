#!/bin/bash

# Script để deploy ứng dụng lên Heroku
# Chạy script này sau khi đã cài đặt Heroku CLI và đăng nhập

echo "🚀 Bắt đầu deploy ứng dụng lên Heroku..."

# Kiểm tra Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI chưa được cài đặt!"
    echo "📥 Hãy cài đặt Heroku CLI:"
    echo "   brew install heroku/brew/heroku"
    echo "   hoặc tải từ: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Kiểm tra đăng nhập
echo "🔐 Kiểm tra đăng nhập Heroku..."
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Chưa đăng nhập Heroku!"
    echo "🔑 Hãy đăng nhập: heroku login"
    exit 1
fi

echo "✅ Đã đăng nhập Heroku: $(heroku auth:whoami)"

# Tạo app Heroku (nếu chưa có)
APP_NAME="fb-ads-dashboard-$(date +%s)"
echo "📱 Tạo app Heroku: $APP_NAME"
heroku create $APP_NAME

# Cấu hình environment variables từ .env file
echo "⚙️  Cấu hình environment variables..."
if [ -f .env ]; then
    # Đọc từng dòng trong .env và set vào Heroku
    while IFS= read -r line || [ -n "$line" ]; do
        # Bỏ qua comment và dòng trống
        if [[ ! $line =~ ^# ]] && [[ ! -z $line ]]; then
            # Loại bỏ khoảng trắng đầu và cuối
            line=$(echo "$line" | xargs)
            # Set environment variable
            heroku config:set "$line" --app $APP_NAME
        fi
    done < .env
    echo "✅ Đã cấu hình environment variables từ .env"
else
    echo "⚠️  Không tìm thấy file .env"
fi

# Cấu hình thêm một số biến môi trường cần thiết
echo "🔧 Cấu hình thêm environment variables..."
heroku config:set FLASK_ENV=production --app $APP_NAME
heroku config:set PYTHONPATH=/app --app $APP_NAME

# Deploy code
echo "📤 Deploy code lên Heroku..."
git add .
git commit -m "Deploy to Heroku - $(date)"
git push heroku main

# Mở ứng dụng
echo "🌐 Mở ứng dụng..."
heroku open --app $APP_NAME

echo "✅ Deploy hoàn tất!"
echo "🔗 URL ứng dụng: https://$APP_NAME.herokuapp.com"
echo "📊 Xem logs: heroku logs --tail --app $APP_NAME"
