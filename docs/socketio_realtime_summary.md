# Tóm Tắt Tầng Realtime Socket.IO

## 1) Các giả định đã xác minh từ code hiện tại

- Truy cập `table_number` trong `Order`:
  - `Order.table_number` là `ForeignKey` tới `Table`.
  - Giá trị số của bàn có thể lấy trực tiếp qua `Order.table_number_id`.
  - Trong project này, `table_number_id` được dùng để tạo room `table_{tableNumber}`.

- `related_name` từ `OrderItem` sang `Order`:
  - Không khai báo `related_name` tường minh trên `OrderItem.order_id`.
  - Reverse accessor mặc định là `orderitem_set`.
  - Socket serializer dùng `source="orderitem_set"`.

- Cấu trúc settings:
  - Project dùng settings tách file:
    - `restaurantBE/settings/common.py`
    - `restaurantBE/settings/local.py`
    - `restaurantBE/settings/production.py`

- Runtime server đang dùng:
  - Script hiện tại chạy Django bằng Gunicorn + WSGI (`restaurantBE.wsgi:application`).
  - Để chạy WebSocket/Socket.IO theo ASGI, cần chạy Uvicorn với `restaurantBE.asgi:application`.

## 2) Các thay đổi đã triển khai

### A. Socket.IO server và Redis manager

Đã cập nhật:
- `restaurantBE/sockets/server.py`

Đã làm:
- Giữ `socketio.AsyncServer(async_mode="asgi")`.
- Cấu hình client manager dùng Redis:
  - `socketio.AsyncRedisManager(url=REDIS_URL)`
- Bổ sung cách lấy `REDIS_URL` an toàn:
  - Ưu tiên `django.conf.settings.REDIS_URL` nếu có.
  - Fallback sang `os.getenv("REDIS_URL", "redis://localhost:6379/0")`.
- Expose `socket_app = socketio.ASGIApp(sio, socketio_path="socket.io")`.

### B. Handler connect/disconnect của Socket.IO

Đã cập nhật:
- `restaurantBE/sockets/events.py`

Đã làm:
- `connect(sid, environ, auth)`:
  - Đọc token từ `auth.token` trước.
  - Fallback sang query string `?token=...`.
  - Decode JWT qua `AccessToken(token).payload`.
  - Điều hướng room đúng theo yêu cầu:
    - `role == "staff"` -> vào room `staff_notifications`
    - `role == "guest"` -> vào room `table_{payload['table_number']}`
  - Lưu session gồm room/role.
  - Từ chối token lỗi bằng `ConnectionRefusedError("invalid token")`.
- `disconnect(sid)`:
  - Rời room đã lưu nếu session tồn tại.
  - Bỏ qua an toàn khi session không tồn tại.

Theo yêu cầu mới nhất:
- Đã xoá block comment dài `Frontend example` khỏi code.

### C. Emit helper cho luồng signal đồng bộ của Django

Đã cập nhật:
- `restaurantBE/sockets/utils.py`

Đã làm:
- `emit_new_order(order_data)`:
  - Dùng `async_to_sync(sio.emit)`
  - Phát event `order_created` tới room `staff_notifications`
- `emit_order_updated(table_number, order_data)`:
  - Dùng `async_to_sync(sio.emit)`
  - Phát event `order_status_updated` tới room `table_{table_number}`

### D. Mount ASGI cho Socket.IO + Django

Đã cập nhật:
- `restaurantBE/asgi.py`

Đã làm:
- Giữ thứ tự khởi tạo Django trước (`get_asgi_application()`).
- Import Socket.IO server sau khi Django sẵn sàng.
- Import `restaurantBE.sockets.events` để đăng ký event handlers.
- Mount ASGI cuối cùng:
  - `/socket.io/*` do Socket.IO xử lý.
  - Các route còn lại chuyển cho Django.

### E. Tích hợp signal `post_save` của Order

Đã cập nhật:
- `restaurantBE/orders/signals.py`

Đã làm:
- Mỗi khi `Order` `post_save`:
  - Serialize payload bằng `OrderSocketSerializer`.
  - Nếu `created=True`: emit `order_created` cho room staff.
  - Nếu update: emit `order_status_updated` cho room bàn qua `instance.table_number_id`.
- Bọc `try/except` để lỗi emit socket không làm hỏng vòng đời request REST.

### F. Đăng ký signal trong `ready()` của app Orders

Trạng thái hiện tại:
- `restaurantBE/orders/apps.py` đã import signals trong `ready()`.

Ghi chú:
- App config đang dùng tên đầy đủ `restaurantBE.orders` và import `restaurantBE.orders.signals`.
- Cách này hợp lệ và đang hoạt động cho đăng ký signal.

### G. Internal Socket serializers cho payload sự kiện

Đã cập nhật:
- `restaurantBE/orders/serializers.py`

Đã làm:
- Thêm/chỉnh internal serializers:
  - `OrderItemSocketSerializer`
    - fields: `id`, `dish_name`, `quantity`, `status`, `price`
    - mapping:
      - `dish_name` từ `dish_snapshot_id.name`
      - `status` từ `item_status`
      - `price` từ `dish_snapshot_id.price`
  - `OrderSocketSerializer`
    - fields: `id`, `table_number`, `status`, `items`, `created_at`
    - `table_number` từ `table_number_id`
    - `items` từ reverse relation `orderitem_set`

### H. Nguồn cấu hình Redis

Đã cập nhật:
- `restaurantBE/settings/common.py`

Đã làm:
- Dùng `os.getenv` theo yêu cầu:
  - `REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")`
- Loại bỏ phần dùng `django-environ` đã thêm trước đó.

### I. Dependencies

Đã cập nhật:
- `requirements.txt`

Đã làm:
- Giữ `python-socketio[asyncio]==5.*`
- Thêm `aioredis==2.*`
- Giữ `uvicorn[standard]`

## 3) Kiểm tra rủi ro circular import

Vòng import tiềm năng đã rà soát:
- `orders.signals` import `sockets.utils`
- `sockets.utils` import `sockets.server`

Vì sao chấp nhận được trong setup hiện tại:
- `orders.signals` được load từ `OrdersConfig.ready()` sau khi app registry đã khởi tạo.
- `sockets.server` không import model Django hay module orders.
- `asgi.py` import `sockets.events` riêng để đăng ký socket handlers.

Kết luận:
- Chưa phát hiện circular import gây block với ranh giới module hiện tại.

## 4) Phần chủ động chưa triển khai ở thời điểm này

- Realtime cho payment/webhook ngân hàng.
- Các sự kiện client -> server bổ sung.
- Chiến lược room theo từng order (`order_{id}`).

## 5) Lệnh chạy khuyến nghị cho realtime ở môi trường dev

Chạy bằng ASGI app (không dùng WSGI) để bật WebSocket:

```bash
uvicorn restaurantBE.asgi:application --host 0.0.0.0 --port 8000 --reload
```

Thiết lập biến môi trường (ví dụ):

```bash
REDIS_URL=redis://localhost:6379/0
```
