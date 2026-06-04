# 🗄️ HƯỚNG DẪN KIỂM TRA DATABASE

## 1️⃣ CÁCH CHẠY HỆ THỐNG VÀI NHẤT (Dùng Docker Compose)

- Mở terminal và đi tới thư mục gốc dự án `CNPM2`
- Chạy lệnh `docker compose up --build`
- Chờ Docker tải image và build frontend/backend
- Khi các containers khởi động xong, kiểm tra thông báo `healthy` / `running`

**Truy cập sau khi chạy:**

- Frontend: `http://localhost` hoặc `http://localhost:3000`
- Backend API: `http://localhost:5000/api`
- Database sẽ được khởi tạo tự động

---

## 2️⃣ KIỂM TRA POSTGRESQL (Dữ Liệu Chính)

### Cách 1: Qua Docker (Dễ Nhất)

- Dùng lệnh `docker exec -it hotel_postgres psql -U hoteluser -d hoteldb`
- Trong psql, gõ `\dt` để liệt kê bảng
- Kiểm tra bảng đã được tạo: `users`, `hotels`, `rooms`, `bookings`, `payments`, `reviews`
- Gõ `\q` để thoát psql

### Cách 2: Xem Dữ Liệu Chi Tiết

- Trong psql, chạy `SELECT id, full_name, email, role FROM users;`
- Chạy `SELECT id, name, city, owner_id FROM hotels;`
- Chạy `SELECT id, name, room_type, price_per_night, hotel_id FROM rooms;`
- Chạy `SELECT id, customer_name, check_in, check_out, status FROM bookings;`

### Cách 3: Seed Dữ Liệu Mẫu

- Chạy `docker exec -it hotel_backend python seed.py`
- Hoặc nếu chạy local backend: `cd backend` và `python seed.py`
- Kiểm tra thông báo thành công từ script seed
- Dùng tài khoản demo sau khi seed:
  - `admin@hotel.com` / `Admin@123`
  - `owner1@hotel.com` / `Owner@123`
  - `owner2@hotel.com` / `Owner@123`
  - `user1@hotel.com` / `User@123`
  - `user2@hotel.com` / `User@123`

---

## 3️⃣ KIỂM TRA MONGODB (Logs & Audit)

### Cách 1: Qua Docker

- Chạy `docker exec -it hotel_mongo mongosh`
- Trong mongosh, gõ `use hotel_logs`
- Chạy `show collections` để xem các collection
- Kiểm tra các collection: `audit_logs`, `request_logs`, `user_activities`

### Cách 2: Xem Dữ Liệu

- Trong mongosh, gõ `db.audit_logs.find().limit(5).pretty()`
- Gõ `db.request_logs.find().limit(5).pretty()`
- Gõ `db.user_activities.find().limit(5).pretty()`
- Gõ `db.audit_logs.getIndexes()` để kiểm tra index

---

## 4️⃣ KIỂM TRA BACKEND API (Dùng Postman/cURL)

### Quick Test with cURL

- Đăng ký user mới bằng `POST http://localhost:5000/api/auth/register`
- Đăng nhập bằng `POST http://localhost:5000/api/auth/login`
- Lấy token và gọi `GET http://localhost:5000/api/auth/me`
- Nếu trả về thông tin user thì API hoạt động

### Import Postman Collection (Khuyến Nghị)

1. Mở Postman
2. Nhấp **Import** → Chọn file `POSTMAN_COLLECTION.json` từ thư mục gốc
3. Chọn environment `Local` → chỉnh `base_url = http://localhost:5000/api`
4. Bắt đầu test các endpoint

---

## 5️⃣ KIỂM TRA TẤT CẢ SERVICES HẠY CHẠY

- Chạy `docker compose ps`
- Kiểm tra trạng thái containers: `postgres`, `mongo`, `backend`, `frontend`, `nginx`
- Đảm bảo các service không báo lỗi khởi động
- Nếu cần, dùng `docker compose logs -f backend` để xem log backend

---

## 6️⃣ CHẠY AUTOMATED TESTS

- Vào container backend hoặc môi trường local backend
- Chạy `pytest tests/ -v`
- Nếu muốn test từng file: `pytest tests/test_auth.py -v`
- Chạy `pytest tests/ --cov=app --cov-report=html` để xem coverage

---

## 7️⃣ DỪNG & DỌN DẸP

- Dùng `docker compose down` để dừng toàn bộ services
- Dùng `docker compose down -v` để xóa cả volumes dữ liệu (nếu muốn reset)
- Dùng `docker compose logs --tail 50` để xem log sau khi tắt
- Xác nhận không còn container đang chạy bằng `docker ps`

---

## ✅ CHECKLIST KIỂM TRA DATABASE

| Bước | Lệnh/Cách | Kết Quả Mong Đợi |
|---|---|---|
| 1 | `docker compose up --build` | Tất cả services chạy |
| 2 | `docker compose ps` | Status = **healthy** hoặc **running** |
| 3 | PostgreSQL: `\dt` | Thấy 6 bảng (users, hotels, rooms, bookings, payments, reviews) |
| 4 | MongoDB: `show collections` | Thấy 3 collections (audit_logs, request_logs, user_activities) |
| 5 | Seed: `python seed.py` | "✅ All seed data inserted successfully!" |
| 6 | cURL/Postman: POST /register | 201 Created + user data |
| 7 | cURL/Postman: POST /login | 200 OK + access_token |
| 8 | cURL/Postman: GET /auth/me | 200 OK + user info |

✅ Nếu tất cả bước trên thành công → **Database & API sẵn sàng!**
