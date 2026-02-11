# Guest JWT Authentication Documentation

## Tổng quan

Hệ thống Guest Authentication cho phép khách hàng tại nhà hàng đăng nhập vào hệ thống bằng cách sử dụng:
- **Tên khách** (name)
- **Số bàn** (tableNumber)
- **Token của bàn** (tableToken)

**Đặc điểm:**
- Login tự động tạo một Guest mới trong database
- Sử dụng JWT (SimpleJWT) giống như Account authentication
- RefreshToken được lưu trong database để quản lý session
- Phân biệt rõ ràng với Account tokens thông qua `user_type` claim

---

## Database Schema

```sql
Table Guest {
  id Int [pk, increment]
  name String [not null]
  tableNumber Int [foreign key -> Table.number]
  refreshToken Text [nullable]
  refreshTokenExpiresAt DateTime [nullable]
  createdAt DateTime [default: now(), not null]
  updatedAt DateTime [not null]
}

Table Table {
  number Int [pk]
  capacity Int [not null]
  status String [not null]
  token String [not null]  -- Secret token để xác thực
  createdAt DateTime
  updatedAt DateTime
}
```

---

## API Endpoints

### 1. Guest Login (Tạo Guest mới)

**Endpoint:** `POST /api/guests/login/`

**Request Body:**
```json
{
  "name": "Nguyễn Văn A",
  "tableNumber": 5,
  "tableToken": "secret_table_5_token"
}
```

**Response (Success - 200):**
```json
{
  "statusCode": 200,
  "message": "guest_login_success",
  "data": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "guest": {
      "id": 123,
      "name": "Nguyễn Văn A",
      "tableNumber": 5,
      "create_at": "2026-02-11T14:00:00Z",
      "update_at": "2026-02-11T14:00:00Z"
    }
  }
}
```

**Response (Error - 422):**
```json
{
  "statusCode": 422,
  "message": "validation_error",
  "errors": {
    "tableToken": ["invalid_table_token"]
  }
}
```

**Validation:**
- `name`: Tối thiểu 2 ký tự
- `tableNumber`: Phải tồn tại trong database
- `tableToken`: Phải khớp với token của bàn

**Flow:**
1. Validate tableNumber và tableToken
2. Tạo Guest mới trong database
3. Generate JWT tokens (refresh + access)
4. Lưu refreshToken vào database
5. Trả về tokens và thông tin guest

---

### 2. Guest Logout

**Endpoint:** `POST /api/guests/logout/`

**Request Body:**
```json
{
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (Success - 200):**
```json
{
  "statusCode": 200,
  "message": "guest_logout_success",
  "data": null
}
```

**Flow:**
1. Verify refreshToken
2. Xóa refreshToken khỏi database (set NULL)
3. Blacklist tất cả tokens của guest
4. Trả về success

---

### 3. Guest Refresh Token

**Endpoint:** `POST /api/guests/refresh-token/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (Success - 200):**
```json
{
  "statusCode": 200,
  "message": "guest_token_refresh_success",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Response (Error - 422):**
```json
{
  "statusCode": 422,
  "message": "validation_error",
  "errors": ["token_expired"]
}
```

**Validation:**
- Verify `user_type` = 'guest'
- Verify guest tồn tại
- Verify refreshToken khớp với database
- Verify token chưa hết hạn

---

## JWT Token Structure

### Access Token Claims
```json
{
  "token_type": "access",
  "exp": 1707656400,
  "iat": 1707652800,
  "jti": "abc123...",
  "user_id": 123,
  "name": "Nguyễn Văn A",
  "tableNumber": 5,
  "user_type": "guest"
}
```

### Refresh Token Claims
```json
{
  "token_type": "refresh",
  "exp": 1708257600,
  "iat": 1707652800,
  "jti": "def456...",
  "user_id": 123,
  "name": "Nguyễn Văn A",
  "tableNumber": 5,
  "user_type": "guest"
}
```

**Quan trọng:** `user_type: "guest"` phân biệt với Account tokens (`user_type: "account"`)

---

## Authentication trong API Requests

### Sử dụng Access Token

```http
GET /api/some-endpoint/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Custom Authentication Classes

Có 3 authentication classes có thể sử dụng:

#### 1. GuestJWTAuthentication
Chỉ chấp nhận Guest tokens
```python
from restaurantBE.authentication import GuestJWTAuthentication

class MyView(APIView):
    authentication_classes = [GuestJWTAuthentication]
    permission_classes = [IsAuthenticated]
```

#### 2. AccountJWTAuthentication
Chỉ chấp nhận Account tokens
```python
from restaurantBE.authentication import AccountJWTAuthentication

class MyView(APIView):
    authentication_classes = [AccountJWTAuthentication]
    permission_classes = [IsAuthenticated]
```

#### 3. UniversalJWTAuthentication
Chấp nhận cả Guest và Account tokens
```python
from restaurantBE.authentication import UniversalJWTAuthentication

class MyView(APIView):
    authentication_classes = [UniversalJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user  # Có thể là Guest hoặc Account
        # Kiểm tra loại user
        if isinstance(user, Guest):
            # Xử lý cho guest
            pass
        elif isinstance(user, Account):
            # Xử lý cho account
            pass
```

---

## Migration

Chạy migration để cập nhật database:

```bash
python manage.py makemigrations guests
python manage.py migrate guests
```

---

## Testing với Postman/cURL

### 1. Login Guest
```bash
curl -X POST http://localhost:8000/api/guests/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Guest",
    "tableNumber": 1,
    "tableToken": "your_table_token"
  }'
```

### 2. Sử dụng Access Token
```bash
curl -X GET http://localhost:8000/api/some-endpoint/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Refresh Token
```bash
curl -X POST http://localhost:8000/api/guests/refresh-token/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### 4. Logout
```bash
curl -X POST http://localhost:8000/api/guests/logout/ \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "YOUR_REFRESH_TOKEN"
  }'
```

---

## Error Messages

| Error Code | Message | Mô tả |
|------------|---------|-------|
| `name_too_short` | Name quá ngắn | Tên phải >= 2 ký tự |
| `table_not_found` | Bàn không tồn tại | tableNumber không hợp lệ |
| `invalid_table_token` | Token bàn không đúng | tableToken sai |
| `guest_not_found` | Guest không tồn tại | Guest ID không tìm thấy |
| `token_expired` | Token hết hạn | refreshToken đã hết hạn |
| `token_mismatch` | Token không khớp | refreshToken không khớp với DB |
| `invalid_guest_token` | Token không phải guest | Token là account token |
| `token_invalid` | Token không hợp lệ | Token bị lỗi hoặc malformed |

---

## Best Practices

1. **Bảo mật tableToken**: Không expose tableToken ra ngoài, chỉ hiển thị QR code tại bàn
2. **Token Expiry**: Cấu hình thời gian hợp lý trong settings.py
3. **Cleanup**: Định kỳ xóa Guest records cũ (có thể dùng Celery task)
4. **Validation**: Luôn validate tableToken trước khi tạo guest
5. **Logging**: Log tất cả guest login/logout để audit

---

## Cấu hình JWT Settings (settings.py)

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

---

## So sánh Guest vs Account Authentication

| Feature | Guest | Account |
|---------|-------|---------|
| Login Method | name + tableNumber + tableToken | email + password |
| Password | Không cần | Bắt buộc |
| Registration | Tự động khi login | Riêng biệt |
| Token Storage | Database (refreshToken field) | OutstandingToken table |
| User Type Claim | `user_type: "guest"` | `user_type: "account"` |
| Session Duration | Ngắn (1 ngày) | Dài hơn |
| Use Case | Khách tại nhà hàng | Nhân viên/Admin |
