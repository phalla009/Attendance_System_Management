from datetime import date, datetime
from flask import render_template
from flask_login import login_required
from sqlalchemy import extract
from extensions import db
from models.attendance import Attendance
from models.user import UserProfile
from . import attendance_bp


@attendance_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    today = date.today()

    total_users = UserProfile.query.count() if hasattr(UserProfile, 'query') else 0

    present_count = Attendance.query.filter(
        Attendance.Status == 'Present',
        db.func.date(Attendance.Date) == today
    ).count()

    late_count = Attendance.query.filter(
        Attendance.Status == 'Late',
        db.func.date(Attendance.Date) == today
    ).count() if hasattr(Attendance, 'Status') else 0

    absent_count = Attendance.query.filter(
        Attendance.Status == 'Absent',
        db.func.date(Attendance.Date) == today
    ).count() if hasattr(Attendance, 'Status') else 0

    present_rate = round((present_count / total_users * 100) if total_users > 0 else 0, 1)
    current_year = datetime.now().year

    monthly_counts = []
    for month in range(1, 13):
        count = Attendance.query.filter(
            extract('year', Attendance.Date) == current_year,
            extract('month', Attendance.Date) == month,
            Attendance.Status == 'Present'
        ).count()
        monthly_counts.append(count)

    time_slots = [8, 10, 12, 14, 16]
    hourly_counts = []
    for hour in time_slots:
        count = Attendance.query.filter(
            extract('hour', Attendance.Date) == hour
        ).count()
        hourly_counts.append(count)

    return render_template(
        'attendance/dashboard.html',
        total_users=total_users or 0,
        present_count=present_count or 0,
        late_count=late_count or 0,
        absent_count=absent_count or 0,
        present_rate=present_rate or 0.0,
        monthly_counts=monthly_counts if monthly_counts else [0] * 12,
        hourly_counts=hourly_counts if hourly_counts else [0] * 5
    )


@attendance_bp.route('/scan/active', methods=['GET'])
@login_required
def active_scan_sessions():
    from models.attendance import QrCode
    now = datetime.now()
    active_qrs = QrCode.query.filter(QrCode.StartDate <= now, QrCode.EndDate >= now).all()
    return render_template('attendance/active_scans.html', active_qrs=active_qrs)