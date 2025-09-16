# Facebook Access Token Test - CURL Commands

## 🔑 Cách sử dụng

Thay thế `YOUR_ACCESS_TOKEN` bằng access token mới của bạn và `YOUR_ACCOUNT_ID` bằng Facebook Account ID của bạn.

## 👤 Test 1: Kiểm tra thông tin user

```bash
curl -s 'https://graph.facebook.com/v18.0/me?access_token=YOUR_ACCESS_TOKEN' | python -m json.tool
```

**Kết quả mong đợi:**
```json
{
  "id": "123456789",
  "name": "Your Name"
}
```

## 🔐 Test 2: Kiểm tra quyền truy cập

```bash
curl -s 'https://graph.facebook.com/v18.0/me/permissions?access_token=YOUR_ACCESS_TOKEN' | python -m json.tool
```

**Kết quả mong đợi:**
```json
{
  "data": [
    {
      "permission": "ads_management",
      "status": "granted"
    },
    {
      "permission": "ads_read",
      "status": "granted"
    }
  ]
}
```

## 📊 Test 3: Kiểm tra tài khoản quảng cáo

```bash
curl -s 'https://graph.facebook.com/v18.0/me/adaccounts?access_token=YOUR_ACCESS_TOKEN&fields=id,name,account_status' | python -m json.tool
```

**Kết quả mong đợi:**
```json
{
  "data": [
    {
      "id": "act_123456789",
      "name": "Your Ad Account",
      "account_status": 1
    }
  ]
}
```

## 🎯 Test 4: Kiểm tra tài khoản cụ thể

```bash
curl -s 'https://graph.facebook.com/v18.0/YOUR_ACCOUNT_ID?access_token=YOUR_ACCESS_TOKEN&fields=id,name,account_status,currency' | python -m json.tool
```

**Kết quả mong đợi:**
```json
{
  "id": "act_123456789",
  "name": "Your Ad Account",
  "account_status": 1,
  "currency": "USD"
}
```

## 📈 Test 5: Kiểm tra campaigns

```bash
curl -s 'https://graph.facebook.com/v18.0/YOUR_ACCOUNT_ID/campaigns?access_token=YOUR_ACCESS_TOKEN&fields=id,name,status&limit=5' | python -m json.tool
```

**Kết quả mong đợi:**
```json
{
  "data": [
    {
      "id": "123456789",
      "name": "Campaign Name",
      "status": "ACTIVE"
    }
  ]
}
```

## 🧪 Test nhanh với token hiện tại

Nếu bạn muốn test token hiện tại trong file `.env`:

```bash
# Lấy token từ .env
TOKEN=$(grep FACEBOOK_ACCESS_TOKEN .env | cut -d'=' -f2)
ACCOUNT_ID=$(grep FACEBOOK_ACCOUNT_IDS .env | cut -d'=' -f2 | cut -d',' -f1)

# Test user info
curl -s "https://graph.facebook.com/v18.0/me?access_token=$TOKEN" | python -m json.tool

# Test ad accounts
curl -s "https://graph.facebook.com/v18.0/me/adaccounts?access_token=$TOKEN&fields=id,name,account_status" | python -m json.tool

# Test specific account
curl -s "https://graph.facebook.com/v18.0/$ACCOUNT_ID?access_token=$TOKEN&fields=id,name,account_status" | python -m json.tool
```

## 📋 Danh sách các endpoints hữu ích khác

### Test Insights
```bash
# Lấy insights của account
curl -s 'https://graph.facebook.com/v18.0/YOUR_ACCOUNT_ID/insights?access_token=YOUR_ACCESS_TOKEN&fields=impressions,clicks,spend&date_preset=last_30d' | python -m json.tool
```

### Test Ad Sets
```bash
# Lấy ad sets
curl -s 'https://graph.facebook.com/v18.0/YOUR_ACCOUNT_ID/adsets?access_token=YOUR_ACCESS_TOKEN&fields=id,name,status&limit=5' | python -m json.tool
```

### Test Ads
```bash
# Lấy ads
curl -s 'https://graph.facebook.com/v18.0/YOUR_ACCOUNT_ID/ads?access_token=YOUR_ACCESS_TOKEN&fields=id,name,status&limit=5' | python -m json.tool
```

## ⚠️ Lưu ý quan trọng

1. **Access Token**: Phải có quyền `ads_management` hoặc `ads_read`
2. **Account ID**: Phải là tài khoản quảng cáo hợp lệ
3. **Rate Limiting**: Facebook có giới hạn số lượng request
4. **Token Expiry**: Access token có thể hết hạn

## 🔍 Debug lỗi thường gặp

### Lỗi 400 Bad Request
- Kiểm tra format của access token
- Kiểm tra các tham số fields

### Lỗi 401 Unauthorized
- Access token đã hết hạn
- Token không có quyền truy cập

### Lỗi 403 Forbidden
- Không có quyền truy cập tài khoản
- Tài khoản bị khóa hoặc hạn chế

### Lỗi 404 Not Found
- Account ID không tồn tại
- Endpoint không đúng

## 🚀 Test tự động

Bạn cũng có thể chạy script test tự động:

```bash
python test_facebook_token.py
```

Script này sẽ hướng dẫn bạn nhập token mới và chạy tất cả các tests.
