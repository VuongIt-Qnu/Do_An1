"""
Database Seed Script — CNPM2 Hotel Management System
======================================================
Tạo dữ liệu mẫu đầy đủ cho development/testing.

Cách chạy:
    # Bên trong container:
    docker exec -it hotel_backend python seed.py

    # Hoặc local:
    python seed.py

Tài khoản demo sau khi seed:
    ADMIN : admin@hotel.com     / Admin@123
    OWNER1: owner1@hotel.com    / Owner@123
    OWNER2: owner2@hotel.com    / Owner@123
    USER1 : user1@hotel.com     / User@123
    USER2 : user2@hotel.com     / User@123
"""
import os
import sys
from datetime import date, timedelta, datetime

# Phải load env trước khi import app
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.user    import User
from app.models.hotel   import Hotel
from app.models.room    import Room
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.review  import Review


def seed_users(app):
    """Tạo 5 users: 1 admin, 2 owner, 2 user"""
    print("  → Seeding users...")

    users_data = [
        dict(full_name="System Admin",    email="admin@hotel.com",  phone_number="+84901000001",
             role="ADMIN",  password="Admin@123"),
        dict(full_name="Nguyễn Văn Hùng", email="owner1@hotel.com", phone_number="+84901000002",
             role="OWNER",  password="Owner@123"),
        dict(full_name="Trần Thị Mai",    email="owner2@hotel.com", phone_number="+84901000003",
             role="OWNER",  password="Owner@123"),
        dict(full_name="Lê Quốc Bảo",    email="user1@hotel.com",  phone_number="+84901000004",
             role="USER",   password="User@123"),
        dict(full_name="Phạm Thị Lan",   email="user2@hotel.com",  phone_number="+84901000005",
             role="USER",   password="User@123"),
    ]

    created_ids = []
    with app.app_context():
        for d in users_data:
            existing = User.query.filter_by(email=d["email"]).first()
            if existing:
                print(f"     ✓ User {d['email']} đã tồn tại, bỏ qua.")
                created_ids.append(existing.id)
                continue

            u = User(
                full_name=d["full_name"],
                email=d["email"],
                phone_number=d["phone_number"],
                role=d["role"],
                enabled=True,
                nationality="Việt Nam",
            )
            u.set_password(d["password"])
            db.session.add(u)
            db.session.flush()  # Lấy id ngay
            created_ids.append(u.id)
            print(f"     ✓ Tạo {d['role']:5} : {d['email']}  mật khẩu: {d['password']}")

        db.session.commit()

    return created_ids


def seed_hotels(app, owner1_id, owner2_id):
    """Tạo 5 khách sạn (3 cho owner1, 2 cho owner2)"""
    print("  → Seeding hotels...")

    # Payment info mẫu cho từng owner
    owner1_payment = dict(
        bank_name="Vietcombank", account_number="1234567890",
        account_holder="NGUYEN VAN HUNG", bank_branch="Chi nhánh Hoàn Kiếm - Hà Nội",
        momo_number="0901000002",
        momo_qr="https://img.vietqr.io/image/VCB-1234567890-compact.png",
        qr_code_url="https://img.vietqr.io/image/VCB-1234567890-qr_only.png",
    )
    owner2_payment = dict(
        bank_name="Techcombank", account_number="9876543210",
        account_holder="TRAN THI MAI", bank_branch="Chi nhánh Quận 1 - TP.HCM",
        momo_number="0901000003",
        momo_qr="https://img.vietqr.io/image/TCB-9876543210-compact.png",
        qr_code_url="https://img.vietqr.io/image/TCB-9876543210-qr_only.png",
    )

    hotels_data = [
        dict(owner_id=owner1_id, name="Grand Palace Hotel",
             city="Hà Nội",      address="123 Lý Thường Kiệt, Hoàn Kiếm",
             phone="+84241234567", email="info@grandpalace.vn", star_rating=5,
             description="Khách sạn 5 sao sang trọng trung tâm Hà Nội, view hồ Hoàn Kiếm.",
             **owner1_payment),
        dict(owner_id=owner1_id, name="Lotus Garden Hotel",
             city="Hà Nội",      address="45 Hàng Bông, Hoàn Kiếm",
             phone="+84241234568", email="info@lotusgarden.vn", star_rating=4,
             description="Khách sạn 4 sao phong cách boutique giữa phố cổ Hà Nội.",
             **owner1_payment),
        dict(owner_id=owner1_id, name="Sunrise Beach Resort",
             city="Đà Nẵng",    address="99 Võ Nguyên Giáp, Mỹ Khê",
             phone="+84511234567", email="info@sunrisebeach.vn", star_rating=5,
             description="Resort 5 sao bên bãi biển Mỹ Khê đẹp nhất hành tinh.",
             **owner1_payment),
        dict(owner_id=owner2_id, name="Saigon Sky Hotel",
             city="TP. Hồ Chí Minh", address="88 Lê Lợi, Quận 1",
             phone="+84281234567", email="info@saigonsky.vn", star_rating=4,
             description="Khách sạn 4 sao trung tâm Sài Gòn, gần Bến Thành.",
             **owner2_payment),
        dict(owner_id=owner2_id, name="Hoi An Ancient Retreat",
             city="Hội An",    address="12 Nguyễn Thị Minh Khai, Minh An",
             phone="+84511234568", email="info@hoianretreat.vn", star_rating=4,
             description="Khách sạn đậm nét văn hoá Hội An cổ, nằm bên sông Thu Bồn.",
             **owner2_payment),
    ]

    created_ids = []
    with app.app_context():
        for d in hotels_data:
            existing = Hotel.query.filter_by(name=d["name"]).first()
            if existing:
                print(f"     ✓ Hotel '{d['name']}' đã tồn tại, bỏ qua.")
                created_ids.append(existing.id)
                continue

            h = Hotel(
                owner_id=d["owner_id"],
                name=d["name"],
                city=d["city"],
                address=d["address"],
                phone=d["phone"],
                email=d["email"],
                star_rating=d["star_rating"],
                description=d["description"],
                enabled=True,
                approved=True,
                bank_name=d.get("bank_name"),
                account_number=d.get("account_number"),
                account_holder=d.get("account_holder"),
                bank_branch=d.get("bank_branch"),
                momo_number=d.get("momo_number"),
                momo_qr=d.get("momo_qr"),
                qr_code_url=d.get("qr_code_url"),
            )
            db.session.add(h)
            db.session.flush()
            created_ids.append(h.id)
            print(f"     ✓ Hotel: {d['name']} ({d['city']}, {d['star_rating']}★)")

        db.session.commit()

    return created_ids


def seed_rooms(app, hotel_ids):
    """Tạo 5 phòng cho mỗi khách sạn"""
    print("  → Seeding rooms...")

    room_templates = [
        dict(name="Standard City View",  room_type="Standard",     capacity=2,
             price_per_night=750000,  area=25,  featured=False,
             amenities="WiFi,AC,TV,Minibar,Tủ lạnh",
             description="Phòng tiêu chuẩn view thành phố, thoáng mát và đầy đủ tiện nghi cơ bản."),
        dict(name="Deluxe Garden View",  room_type="Deluxe",       capacity=2,
             price_per_night=1200000, area=35,  featured=True,
             amenities="WiFi,AC,TV,Minibar,Bathtub,Balcony,Coffee Maker",
             description="Phòng Deluxe view vườn xanh, ban công riêng và bồn tắm thư giãn."),
        dict(name="Family Room",         room_type="Family",        capacity=4,
             price_per_night=1800000, area=50,  featured=False,
             amenities="WiFi,AC,TV,Minibar,Kitchen,Washing Machine,Sofa",
             description="Phòng gia đình rộng rãi với bếp nhỏ và máy giặt tiện lợi."),
        dict(name="Junior Suite",        room_type="Suite",         capacity=2,
             price_per_night=2500000, area=60,  featured=True,
             amenities="WiFi,AC,TV,Minibar,Jacuzzi,Living Room,Balcony,Butler on call",
             description="Suite hạng nhỏ với phòng khách riêng, bồn Jacuzzi và ban công hướng đẹp."),
        dict(name="Presidential Suite",  room_type="Presidential",  capacity=4,
             price_per_night=6000000, area=120, featured=True,
             amenities="WiFi,AC,TV,Minibar,Jacuzzi,Living Room,Kitchen,Balcony,Butler 24/7,Gym access",
             description="Phòng tổng thống đỉnh cao sang trọng với dịch vụ butler 24/7 và tiện nghi đẳng cấp."),
    ]

    created_ids = []
    with app.app_context():
        for hotel_id in hotel_ids:
            h = db.session.get(Hotel, hotel_id)
            existing_count = h.rooms.count()

            if existing_count >= len(room_templates):
                print(f"     ✓ Hotel '{h.name}' đã có {existing_count} phòng, bỏ qua.")
                created_ids.extend([r.id for r in h.rooms.all()])
                continue

            for tmpl in room_templates:
                r = Room(
                    hotel_id=h.id,
                    name=tmpl["name"],
                    room_type=tmpl["room_type"],
                    capacity=tmpl["capacity"],
                    price_per_night=tmpl["price_per_night"],
                    area=tmpl["area"],
                    amenities=tmpl["amenities"],
                    description=tmpl["description"],
                    featured=tmpl["featured"],
                    status="AVAILABLE",
                    rating=4.5,
                )
                db.session.add(r)
                db.session.flush()
                created_ids.append(r.id)

            print(f"     ✓ {len(room_templates)} phòng → Hotel '{h.name}'")

        db.session.commit()

    return created_ids


def seed_bookings_and_payments(app, user_ids, hotel_ids, room_ids):
    """Tạo 5 bookings mẫu với payments"""
    print("  → Seeding bookings & payments...")

    # Lấy user1 và user2 (index 3, 4)
    # Lấy hotel đầu tiên với các phòng của nó

    booking_samples = [
        dict(user_idx=3, hotel_idx=0, room_idx=0,
             customer_name="Lê Quốc Bảo",    customer_email="user1@hotel.com", customer_phone="+84901000004",
             check_in=date.today() - timedelta(days=30), check_out=date.today() - timedelta(days=28),
             guests=2, notes="Nhờ chuẩn bị hoa tươi trong phòng.", status="COMPLETED",
             payment_status="PAID"),
        dict(user_idx=4, hotel_idx=1, room_idx=1,
             customer_name="Phạm Thị Lan",   customer_email="user2@hotel.com", customer_phone="+84901000005",
             check_in=date.today() - timedelta(days=15), check_out=date.today() - timedelta(days=13),
             guests=2, notes="Phòng trên tầng cao.", status="COMPLETED",
             payment_status="PAID"),
        dict(user_idx=3, hotel_idx=2, room_idx=2,
             customer_name="Lê Quốc Bảo",    customer_email="user1@hotel.com", customer_phone="+84901000004",
             check_in=date.today() + timedelta(days=5),  check_out=date.today() + timedelta(days=8),
             guests=4, notes="", status="CONFIRMED",
             payment_status="PAID"),
        dict(user_idx=4, hotel_idx=3, room_idx=3,
             customer_name="Phạm Thị Lan",   customer_email="user2@hotel.com", customer_phone="+84901000005",
             check_in=date.today() + timedelta(days=10), check_out=date.today() + timedelta(days=12),
             guests=2, notes="Late check-in khoảng 22h.", status="PENDING",
             payment_status="PENDING"),
        dict(user_idx=3, hotel_idx=4, room_idx=4,
             customer_name="Lê Quốc Bảo",    customer_email="user1@hotel.com", customer_phone="+84901000004",
             check_in=date.today() - timedelta(days=60), check_out=date.today() - timedelta(days=58),
             guests=2, notes="", status="CANCELLED",
             payment_status="REFUNDED"),
    ]

    with app.app_context():
        for i, s in enumerate(booking_samples):
            # Kiểm tra đã có chưa
            if Booking.query.count() > i:
                print(f"     ✓ Booking #{i+1} đã tồn tại, bỏ qua.")
                continue

            u = db.session.get(User,  user_ids[s["user_idx"]])
            h = db.session.get(Hotel, hotel_ids[s["hotel_idx"]])
            r = db.session.get(Room,  room_ids[s["hotel_idx"] * 5 + s["room_idx"]])

            nights = (s["check_out"] - s["check_in"]).days
            price  = float(r.price_per_night) * nights

            booking = Booking(
                user_id=u.id,
                customer_name=s["customer_name"],
                customer_email=s["customer_email"],
                customer_phone=s["customer_phone"],
                hotel_id=h.id,
                room_id=r.id,
                check_in=s["check_in"],
                check_out=s["check_out"],
                guests=s["guests"],
                total_price=price,
                status=s["status"],
                notes=s["notes"],
            )
            db.session.add(booking)
            db.session.flush()

            payment = Payment(
                booking_id=booking.id,
                amount=price,
                method="BANK_TRANSFER",
                status=s["payment_status"],
                paid_at=datetime.utcnow() if s["payment_status"] == "PAID" else None,
                transaction_ref=f"TXN-SEED-{i+1:04d}" if s["payment_status"] in ("PAID", "REFUNDED") else None,
            )
            db.session.add(payment)
            db.session.flush()

            # Nếu COMPLETED → đánh dấu phòng lại (status không đổi vì đã check-out)
            # Nếu CONFIRMED → phòng đang được đặt trước (tương lai)
            if s["status"] == "CONFIRMED" and s["check_in"] <= date.today():
                r.status = "OCCUPIED"

            print(f"     ✓ Booking #{i+1}: {s['customer_name']} @ {h.name} "
                  f"({s['check_in']} ~ {s['check_out']}) [{s['status']}]")

        db.session.commit()


def seed_reviews(app):
    """Tạo 5 reviews cho các booking COMPLETED"""
    print("  → Seeding reviews...")

    with app.app_context():
        completed_bookings = Booking.query.filter_by(status="COMPLETED").all()

        if not completed_bookings:
            print("     ✗ Không có booking COMPLETED để review.")
            return

        review_data = [
            dict(rating=5, comment="Khách sạn tuyệt vời! Phòng rộng, sạch sẽ và nhân viên rất thân thiện. "
                                   "Bữa sáng ngon, view đẹp. Nhất định sẽ quay lại!"),
            dict(rating=4, comment="Phòng đẹp, vị trí thuận tiện. Dịch vụ tốt nhưng bữa sáng hơi ít lựa chọn. "
                                   "Nhìn chung rất hài lòng, sẽ giới thiệu cho bạn bè."),
            dict(rating=5, comment="Resort đẳng cấp 5 sao! Bãi biển riêng tuyệt đẹp, dịch vụ chu đáo. "
                                   "Phòng sạch và tiện nghi. Giá cả phù hợp với chất lượng."),
            dict(rating=3, comment="Phòng ổn, sạch sẽ. Vị trí tốt. Tuy nhiên tiếng ồn từ đường phố "
                                   "hơi nhiều vào buổi tối. Dịch vụ có thể cải thiện thêm."),
            dict(rating=4, comment="Không gian yên tĩnh và thơ mộng, rất phù hợp cho kỳ nghỉ lãng mạn. "
                                   "Phòng được trang trí đẹp theo phong cách Hội An cổ kính."),
        ]

        for i, booking in enumerate(completed_bookings[:5]):
            if Review.query.filter_by(booking_id=booking.id).first():
                print(f"     ✓ Review cho booking #{booking.id} đã tồn tại, bỏ qua.")
                continue

            rv = review_data[i % len(review_data)]
            review = Review(
                booking_id=booking.id,
                user_id=booking.user_id,
                room_id=booking.room_id,
                rating=rv["rating"],
                comment=rv["comment"],
            )
            db.session.add(review)
            db.session.flush()

            # Cập nhật rating trung bình cho phòng
            import sqlalchemy as sa
            avg = db.session.query(sa.func.avg(Review.rating)).filter_by(
                room_id=booking.room_id
            ).scalar()
            room = db.session.get(Room, booking.room_id)
            if room and avg:
                room.rating = round(float(avg), 2)

            print(f"     ✓ Review {rv['rating']}★ cho booking #{booking.id} (room #{booking.room_id})")

        db.session.commit()


def main():
    print("=" * 60)
    print("  CNPM2 — Database Seed Script")
    print("=" * 60)

    env = os.getenv("FLASK_ENV", "development")
    app = create_app(env)

    # ── Step 1: Users ──────────────────────────────────────────────
    user_ids = seed_users(app)
    if not user_ids or len(user_ids) < 5:
        print("  ✗ Không đủ users để seed data.")
        sys.exit(1)

    # ── Step 2: Hotels ─────────────────────────────────────────────
    hotel_ids = seed_hotels(app, owner1_id=user_ids[1], owner2_id=user_ids[2])

    # ── Step 3: Rooms ──────────────────────────────────────────────
    room_ids = seed_rooms(app, hotel_ids)

    # ── Step 4: Bookings & Payments ────────────────────────────────
    seed_bookings_and_payments(app, user_ids, hotel_ids, room_ids)

    # ── Step 5: Reviews ────────────────────────────────────────────
    seed_reviews(app)

    print("=" * 60)
    print("  ✅  Seed hoàn tất!")
    print("")
    print("  Tài khoản demo:")
    print("    ADMIN  : admin@hotel.com   / Admin@123")
    print("    OWNER1 : owner1@hotel.com  / Owner@123")
    print("    OWNER2 : owner2@hotel.com  / Owner@123")
    print("    USER1  : user1@hotel.com   / User@123")
    print("    USER2  : user2@hotel.com   / User@123")
    print("=" * 60)


if __name__ == "__main__":
    main()
