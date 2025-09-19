#!/bin/bash

# Script deploy sửa lỗi - sử dụng app có sẵn hoặc tạo với tên cố định
echo "🚀 Deploy ứng dụng lên Heroku (phiên bản sửa lỗi)..."

# Kiểm tra Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI chưa được cài đặt!"
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

# Tên app cố định (bạn có thể thay đổi)
APP_NAME="fb-ads-dashboard-khuong"

# Kiểm tra xem app đã tồn tại chưa
echo "🔍 Kiểm tra app $APP_NAME..."
if heroku apps:info --app $APP_NAME &> /dev/null; then
    echo "✅ App $APP_NAME đã tồn tại"
else
    echo "📱 Tạo app mới: $APP_NAME"
    if ! heroku create $APP_NAME; then
        echo "❌ Không thể tạo app. Có thể do:"
        echo "   1. Chưa xác minh tài khoản Heroku"
        echo "   2. Tên app đã được sử dụng"
        echo ""
        echo "🔧 Giải pháp:"
        echo "   1. Truy cập https://heroku.com/verify để xác minh tài khoản"
        echo "   2. Hoặc tạo app thủ công trên dashboard Heroku"
        echo "   3. Sau đó chạy lại script này"
        exit 1
    fi
fi

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
            echo "Setting: $line"
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

# Thêm remote Heroku vào git
echo "🔗 Thêm Heroku remote..."
if ! git remote | grep -q heroku; then
    git remote add heroku https://git.heroku.com/$APP_NAME.git
fi

# Deploy code
echo "📤 Deploy code lên Heroku..."
git add .
git commit -m "Deploy to Heroku - $(date)" || echo "Không có thay đổi để commit"

# Push to Heroku
echo "🚀 Pushing to Heroku..."
git push heroku main

# Scale web dyno
echo "📈 Scale web dyno..."
heroku ps:scale web=1 --app $APP_NAME

# Mở ứng dụng
echo "🌐 Mở ứng dụng..."
heroku open --app $APP_NAME

echo "✅ Deploy hoàn tất!"
echo "🔗 URL ứng dụng: https://$APP_NAME.herokuapp.com"
echo "📊 Xem logs: heroku logs --tail --app $APP_NAME"
