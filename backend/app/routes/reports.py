"""
Reports Routes — /api/reports
========================================
Báo cáo doanh thu và thống kê. ADMIN xem toàn hệ thống, OWNER chỉ xem hotel của mình.

GET    /revenue          Doanh thu theo period (daily|monthly|yearly)
GET    /occupancy        Tỷ lệ lấp đầy phòng theo khách sạn
GET    /bookings         Thống kê tổng hợp booking
GET    /export/pdf       Xuất báo cáo PDF (ReportLab)
GET    /export/excel     Xuất báo cáo Excel (openpyxl)
"""
import io
from datetime import date, datetime
from flask import Blueprint, request, send_file
import sqlalchemy as sa

from ..extensions import db
from ..models.booking import Booking
from ..models.hotel import Hotel
from ..models.room import Room
from ..utils.response_helpers import success_response, error_response
from ..middleware.auth_middleware import role_required, get_current_user

reports_bp = Blueprint("reports", __name__)


def _accessible_hotel_ids(user) -> list[int] | None:
    """
    ADMIN → None (không filter, tức là toàn hệ thống).
    OWNER → list hotel_id của owner đó.
    """
    if user.role == "ADMIN":
        return None
    return [h.id for h in Hotel.query.filter_by(owner_id=user.id, enabled=True).all()]


def _apply_hotel_filter(query, hotel_ids):
    """Áp dụng bộ lọc hotel_ids nếu không phải ADMIN."""
    if hotel_ids is not None:
        query = query.filter(Booking.hotel_id.in_(hotel_ids))
    return query


# ── GET /api/reports/revenue ────────────────────────────────────────────────
@reports_bp.route("/revenue", methods=["GET"])
@role_required("ADMIN", "OWNER")
def revenue_report():
    """
    Báo cáo doanh thu nhóm theo period.
    Query params:
        period      — daily | monthly | yearly (mặc định: monthly)
        from_date   — YYYY-MM-DD (mặc định: đầu tháng hiện tại)
        to_date     — YYYY-MM-DD (mặc định: hôm nay)
        hotel_id    — lọc theo khách sạn cụ thể
    """
    user      = get_current_user()
    hotel_ids = _accessible_hotel_ids(user)

    period       = request.args.get("period", "monthly").lower()
    from_date_str = request.args.get("from_date", date.today().replace(day=1).isoformat())
    to_date_str   = request.args.get("to_date", date.today().isoformat())
    hotel_id_filter = request.args.get("hotel_id", type=int)

    try:
        from_date = date.fromisoformat(from_date_str)
        to_date   = date.fromisoformat(to_date_str)
    except ValueError:
        return error_response("Định dạng ngày không hợp lệ. Dùng YYYY-MM-DD", 400)

    if from_date > to_date:
        return error_response("from_date phải nhỏ hơn hoặc bằng to_date", 400)

    # Cột period theo loại báo cáo
    if period == "daily":
        period_col = sa.cast(Booking.check_in, sa.Date).label("period")
        group_col  = sa.cast(Booking.check_in, sa.Date)
    elif period == "yearly":
        period_col = sa.extract("year", Booking.check_in).label("period")
        group_col  = sa.extract("year", Booking.check_in)
    else:  # monthly (default)
        period_col = sa.func.to_char(Booking.check_in, "YYYY-MM").label("period")
        group_col  = sa.func.to_char(Booking.check_in, "YYYY-MM")

    query = db.session.query(
        Booking.hotel_id,
        sa.func.sum(Booking.total_price).label("revenue"),
        sa.func.count(Booking.id).label("count"),
        period_col,
    ).filter(
        Booking.status.in_(["CONFIRMED", "COMPLETED"]),
        sa.cast(Booking.check_in, sa.Date) >= from_date,
        sa.cast(Booking.check_in, sa.Date) <= to_date,
    ).group_by(Booking.hotel_id, group_col).order_by(group_col)

    query = _apply_hotel_filter(query, hotel_ids)
    if hotel_id_filter:
        query = query.filter(Booking.hotel_id == hotel_id_filter)

    results = query.all()

    records = [{
        "period":         str(r.period),
        "hotel_id":       r.hotel_id,
        "revenue":        float(r.revenue or 0),
        "bookings_count": r.count,
    } for r in results]

    total_revenue = sum(r["revenue"] for r in records)

    return success_response(data={
        "period":        period,
        "from_date":     from_date_str,
        "to_date":       to_date_str,
        "total_revenue": total_revenue,
        "records":       records,
    })


# ── GET /api/reports/occupancy ──────────────────────────────────────────────
@reports_bp.route("/occupancy", methods=["GET"])
@role_required("ADMIN", "OWNER")
def occupancy_report():
    """Tỷ lệ lấp đầy phòng theo từng khách sạn."""
    user      = get_current_user()
    hotel_ids = _accessible_hotel_ids(user)

    query = db.session.query(
        Hotel.id,
        Hotel.name,
        Hotel.city,
        sa.func.count(Room.id).label("total_rooms"),
        sa.func.sum(
            sa.case((Room.status == "OCCUPIED", 1), else_=0)
        ).label("occupied_rooms"),
        sa.func.sum(
            sa.case((Room.status == "AVAILABLE", 1), else_=0)
        ).label("available_rooms"),
    ).outerjoin(Room, Room.hotel_id == Hotel.id).filter(
        Hotel.enabled == True
    ).group_by(Hotel.id, Hotel.name, Hotel.city)

    if hotel_ids is not None:
        query = query.filter(Hotel.id.in_(hotel_ids))

    results = query.all()

    data = []
    for r in results:
        total    = r.total_rooms or 0
        occupied = r.occupied_rooms or 0
        rate     = round(occupied / total * 100, 2) if total > 0 else 0
        data.append({
            "hotel_id":        r.id,
            "hotel_name":      r.name,
            "city":            r.city,
            "total_rooms":     total,
            "occupied_rooms":  occupied,
            "available_rooms": r.available_rooms or 0,
            "occupancy_rate":  rate,
        })

    # Sắp xếp theo tỷ lệ lấp đầy giảm dần
    data.sort(key=lambda x: x["occupancy_rate"], reverse=True)

    overall_total    = sum(d["total_rooms"] for d in data)
    overall_occupied = sum(d["occupied_rooms"] for d in data)
    overall_rate     = round(overall_occupied / overall_total * 100, 2) if overall_total else 0

    return success_response(data={
        "overall_occupancy_rate": overall_rate,
        "total_hotels":           len(data),
        "hotel_occupancy":        data,
    })


# ── GET /api/reports/bookings ───────────────────────────────────────────────
@reports_bp.route("/bookings", methods=["GET"])
@role_required("ADMIN", "OWNER")
def booking_report():
    """
    Thống kê tổng hợp booking.
    Query params: hotel_id, from_date, to_date
    """
    user      = get_current_user()
    hotel_ids = _accessible_hotel_ids(user)

    hotel_id_filter = request.args.get("hotel_id", type=int)
    from_date_str   = request.args.get("from_date")
    to_date_str     = request.args.get("to_date")

    query = Booking.query
    query = _apply_hotel_filter(query, hotel_ids)

    if hotel_id_filter:
        query = query.filter(Booking.hotel_id == hotel_id_filter)
    if from_date_str:
        try:
            query = query.filter(Booking.created_at >= date.fromisoformat(from_date_str))
        except ValueError:
            pass
    if to_date_str:
        try:
            query = query.filter(Booking.created_at <= date.fromisoformat(to_date_str))
        except ValueError:
            pass

    total_bookings = query.count()

    # Tính từng trạng thái từ query cơ sở (tránh filter mutation)
    pending   = query.filter(Booking.status == "PENDING").count()
    confirmed = query.filter(Booking.status == "CONFIRMED").count()
    completed = query.filter(Booking.status == "COMPLETED").count()
    cancelled = query.filter(Booking.status == "CANCELLED").count()

    # Doanh thu trung bình mỗi booking (chỉ tính booking có giá trị)
    avg_value_result = db.session.query(
        sa.func.avg(Booking.total_price)
    )
    if hotel_ids is not None:
        avg_value_result = avg_value_result.filter(Booking.hotel_id.in_(hotel_ids))
    if hotel_id_filter:
        avg_value_result = avg_value_result.filter(Booking.hotel_id == hotel_id_filter)
    avg_booking_value = float(avg_value_result.scalar() or 0)

    total_revenue = float(
        db.session.query(sa.func.sum(Booking.total_price))
        .filter(
            Booking.status.in_(["CONFIRMED", "COMPLETED"]),
            *([] if hotel_ids is None else [Booking.hotel_id.in_(hotel_ids)])
        ).scalar() or 0
    )

    return success_response(data={
        "total_bookings":      total_bookings,
        "pending":             pending,
        "confirmed":           confirmed,
        "completed":           completed,
        "cancelled":           cancelled,
        "total_revenue":       total_revenue,
        "average_booking_value": round(avg_booking_value, 2),
        "completion_rate": round(completed / total_bookings * 100, 2) if total_bookings else 0,
        "cancellation_rate": round(cancelled / total_bookings * 100, 2) if total_bookings else 0,
    })


# ── GET /api/reports/export/pdf ─────────────────────────────────────────────
@reports_bp.route("/export/pdf", methods=["GET"])
@role_required("ADMIN", "OWNER")
def export_pdf():
    """
    Xuất báo cáo doanh thu dạng PDF.
    Query params: from_date, to_date
    Yêu cầu: pip install reportlab
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
    except ImportError:
        return error_response("ReportLab chưa được cài đặt. Chạy: pip install reportlab", 500)

    user      = get_current_user()
    hotel_ids = _accessible_hotel_ids(user)

    from_date_str = request.args.get("from_date", "2020-01-01")
    to_date_str   = request.args.get("to_date", date.today().isoformat())

    try:
        from_date = date.fromisoformat(from_date_str)
        to_date   = date.fromisoformat(to_date_str)
    except ValueError:
        return error_response("Định dạng ngày không hợp lệ. Dùng YYYY-MM-DD", 400)

    query = db.session.query(
        Hotel.name.label("hotel_name"),
        sa.func.to_char(Booking.check_in, "YYYY-MM").label("month"),
        sa.func.count(Booking.id).label("count"),
        sa.func.sum(Booking.total_price).label("revenue"),
    ).join(Hotel, Booking.hotel_id == Hotel.id).filter(
        Booking.status.in_(["CONFIRMED", "COMPLETED"]),
        sa.cast(Booking.check_in, sa.Date) >= from_date,
        sa.cast(Booking.check_in, sa.Date) <= to_date,
    ).group_by(
        Hotel.name, sa.func.to_char(Booking.check_in, "YYYY-MM")
    ).order_by("month", "hotel_name")

    if hotel_ids is not None:
        query = query.filter(Booking.hotel_id.in_(hotel_ids))

    records = query.all()

    # ── Tạo PDF ──
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles   = getSampleStyleSheet()
    elements = []

    # Tiêu đề
    elements.append(Paragraph("Báo Cáo Doanh Thu Khách Sạn", styles["Title"]))
    elements.append(Paragraph(
        f"Từ {from_date_str} đến {to_date_str} | "
        f"Xuất lúc: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 0.5*cm))

    # Bảng dữ liệu
    header    = ["Khách Sạn", "Tháng", "Số Booking", "Doanh Thu (VNĐ)"]
    table_data = [header]
    total_rev  = 0.0

    for r in records:
        rev = float(r.revenue or 0)
        total_rev += rev
        table_data.append([
            r.hotel_name,
            str(r.month),
            str(r.count),
            f"{rev:,.0f}",
        ])

    # Dòng tổng cộng
    table_data.append(["TỔNG CỘNG", "", str(sum(r.count for r in records)), f"{total_rev:,.0f}"])

    col_widths = [7*cm, 3*cm, 3*cm, 4.5*cm]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND",   (0, 0), (-1, 0),  colors.HexColor("#1565C0")),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  11),
        ("ALIGN",        (0, 0), (-1, 0),  "CENTER"),
        # Data rows
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 10),
        ("ALIGN",        (2, 1), (-1, -1), "RIGHT"),
        # Total row
        ("BACKGROUND",   (0, -1), (-1, -1), colors.HexColor("#E3F2FD")),
        ("FONTNAME",     (0, -1), (-1, -1), "Helvetica-Bold"),
        # Grid
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"revenue_report_{date.today().isoformat()}.pdf",
    )


# ── GET /api/reports/export/excel ───────────────────────────────────────────
@reports_bp.route("/export/excel", methods=["GET"])
@role_required("ADMIN", "OWNER")
def export_excel():
    """
    Xuất báo cáo doanh thu dạng Excel (.xlsx).
    Query params: from_date, to_date
    Yêu cầu: pip install openpyxl
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        return error_response("openpyxl chưa được cài đặt. Chạy: pip install openpyxl", 500)

    user      = get_current_user()
    hotel_ids = _accessible_hotel_ids(user)

    from_date_str = request.args.get("from_date", "2020-01-01")
    to_date_str   = request.args.get("to_date", date.today().isoformat())

    try:
        from_date = date.fromisoformat(from_date_str)
        to_date   = date.fromisoformat(to_date_str)
    except ValueError:
        return error_response("Định dạng ngày không hợp lệ. Dùng YYYY-MM-DD", 400)

    query = db.session.query(
        Hotel.name.label("hotel_name"),
        Hotel.city.label("city"),
        sa.func.to_char(Booking.check_in, "YYYY-MM").label("month"),
        sa.func.count(Booking.id).label("count"),
        sa.func.sum(Booking.total_price).label("revenue"),
    ).join(Hotel, Booking.hotel_id == Hotel.id).filter(
        Booking.status.in_(["CONFIRMED", "COMPLETED"]),
        sa.cast(Booking.check_in, sa.Date) >= from_date,
        sa.cast(Booking.check_in, sa.Date) <= to_date,
    ).group_by(
        Hotel.name, Hotel.city, sa.func.to_char(Booking.check_in, "YYYY-MM")
    ).order_by("month", "hotel_name")

    if hotel_ids is not None:
        query = query.filter(Booking.hotel_id.in_(hotel_ids))

    records = query.all()

    # ── Tạo Workbook ──
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Revenue Report"

    # Màu sắc
    BLUE_FILL = PatternFill(start_color="1565C0", end_color="1565C0", fill_type="solid")
    LIGHT_FILL = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"),  bottom=Side(style="thin"),
    )

    # Tiêu đề báo cáo
    ws.merge_cells("A1:E1")
    ws["A1"].value     = "BÁO CÁO DOANH THU KHÁCH SẠN"
    ws["A1"].font      = Font(bold=True, size=14, color="1565C0")
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:E2")
    ws["A2"].value     = f"Từ {from_date_str} đến {to_date_str} | Xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws["A2"].alignment = Alignment(horizontal="center")
    ws["A2"].font      = Font(italic=True, size=10)

    # Headers
    headers = ["Khách Sạn", "Thành Phố", "Tháng", "Số Booking", "Doanh Thu (VNĐ)"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx)
        cell.value     = header
        cell.font      = Font(bold=True, color="FFFFFF", size=11)
        cell.fill      = BLUE_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = thin_border

    ws.row_dimensions[4].height = 20

    # Dữ liệu
    total_bookings = 0
    total_revenue  = 0.0

    for row_idx, r in enumerate(records, 5):
        rev = float(r.revenue or 0)
        total_bookings += r.count
        total_revenue  += rev

        fill = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid") \
               if row_idx % 2 == 0 else None

        values = [r.hotel_name, r.city, r.month, r.count, rev]
        for col_idx, val in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.value  = val
            cell.border = thin_border
            if col_idx >= 4:
                cell.alignment = Alignment(horizontal="right")
            if fill:
                cell.fill = fill
            if col_idx == 5:
                cell.number_format = '#,##0'

    # Dòng tổng cộng
    total_row = len(records) + 5
    ws.cell(row=total_row, column=1).value     = "TỔNG CỘNG"
    ws.cell(row=total_row, column=1).font      = Font(bold=True)
    ws.cell(row=total_row, column=4).value     = total_bookings
    ws.cell(row=total_row, column=5).value     = total_revenue
    ws.cell(row=total_row, column=5).number_format = '#,##0'
    for col_idx in range(1, 6):
        ws.cell(row=total_row, column=col_idx).fill   = LIGHT_FILL
        ws.cell(row=total_row, column=col_idx).border = thin_border
        ws.cell(row=total_row, column=col_idx).font   = Font(bold=True)

    # Auto-fit độ rộng cột
    col_widths = [30, 15, 10, 14, 20]
    for col_idx, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Lưu vào buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"revenue_report_{date.today().isoformat()}.xlsx",
    )
