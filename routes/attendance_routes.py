from datetime import datetime, date
from extensions import db
from flask import Blueprint, flash, redirect, render_template, url_for, request, jsonify
from sqlalchemy import extract
from models.academic import Session, Class, Group, Subject
from models.attendance import Attendance, QrCode
from models.user import UserProfile, UserType
from forms.attendance_form import AttendanceForm
from wtforms import SelectField, StringField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_login import login_required, current_user

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


class QrCodeForm(FlaskForm):
    SessionID = SelectField('Session', coerce=int, validators=[DataRequired()])
    ClassID = SelectField('Class', coerce=int, validators=[DataRequired()])
    GroupID = SelectField('Group', coerce=int, validators=[DataRequired()])
    SubjectID = SelectField('Subject', coerce=int, validators=[DataRequired()])
    StartDate = StringField('Start Date & Time', validators=[DataRequired()])
    EndDate = StringField('End Date & Time', validators=[DataRequired()])


# 1. New Dashboard Route matching the UI Layout
@attendance_bp.route('/dashboard', methods=['GET'])
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


# 2. Existing QR Code Management Route
@attendance_bp.route('/qrcodes', methods=['GET', 'POST'])
def manage_qrcodes():
    form = QrCodeForm()
    form.SessionID.choices = [(s.SessionID, s.Session_name) for s in Session.query.all()]
    form.ClassID.choices = [(c.ClassID, c.Name) for c in Class.query.all()]
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.SubjectID.choices = [(s.SubjectID, s.Name) for s in Subject.query.all()]

    if form.validate_on_submit():
        try:
            start_dt = datetime.strptime(form.StartDate.data, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(form.EndDate.data, '%Y-%m-%dT%H:%M')

            qr = QrCode(
                SessionID=form.SessionID.data,
                SubjectID=form.SubjectID.data,
                StartDate=start_dt,
                EndDate=end_dt,
            )
            db.session.add(qr)
            db.session.commit()
            flash('QR Code session created successfully!', 'success')
            return redirect(url_for('attendance.manage_qrcodes'))
        except ValueError as e:
            flash(f'Date format error: {e}', 'danger')

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Validation Error [{field}]: {error}', 'danger')

    qrcodes = QrCode.query.all()
    return render_template('attendance/qrcodes.html', form=form, qrcodes=qrcodes)


# ----------------- QR CODES (EDIT & DELETE) -----------------
@attendance_bp.route('/qrcodes/edit/<int:id>', methods=['POST'])
def edit_qrcode(id):
    qr = QrCode.query.get_or_404(id)
    form = QrCodeForm()

    form.SessionID.choices = [(s.SessionID, s.Session_name) for s in Session.query.all()]
    form.ClassID.choices = [(c.ClassID, c.Name) for c in Class.query.all()]
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.SubjectID.choices = [(s.SubjectID, s.Name) for s in Subject.query.all()]

    if form.validate_on_submit():
        try:
            qr.SessionID = form.SessionID.data
            qr.SubjectID = form.SubjectID.data
            qr.StartDate = datetime.strptime(form.StartDate.data, '%Y-%m-%dT%H:%M')
            qr.EndDate = datetime.strptime(form.EndDate.data, '%Y-%m-%dT%H:%M')

            db.session.commit()
            flash('QR Code session updated successfully!', 'success')
            return redirect(url_for('attendance.manage_qrcodes'))
        except ValueError as e:
            flash(f'Date format error: {e}', 'danger')

    qrcodes = QrCode.query.all()
    flash('Failed to update QR Code. Please check your inputs.', 'danger')
    return render_template('attendance/qrcodes.html', form=form, qrcodes=qrcodes, edit_error_id=id)


@attendance_bp.route('/qrcodes/delete/<int:id>', methods=['POST'])
def delete_qrcode(id):
    qr = QrCode.query.get_or_404(id)
    try:
        db.session.delete(qr)
        db.session.commit()
        flash('QR Code session deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this QR Code because it is linked to attendance records!', 'danger')

    return redirect(url_for('attendance.manage_qrcodes'))


# API Route to get students filtered by group ID
@attendance_bp.route('/api/students/<int:group_id>', methods=['GET'])
def get_students_by_group(group_id):
    # កែសម្រួល .filter(...) ទៅតាម Column ជាក់ស្តែងក្នុង Model របស់អ្នកដែលផ្ទុក GroupID របស់ UserProfile
    students = UserProfile.query.join(UserType).filter(
        UserType.TypeName == 'Student',
        UserProfile.GroupID == group_id
    ).all()

    result = [{'ProfileID': u.ProfileID, 'Name': u.Name} for u in students]
    return jsonify(result)


# 3. Attendance Records Management Route (With Pagination)
@attendance_bp.route('/records', methods=['GET', 'POST'])
def manage_attendances():
    form = AttendanceForm()

    # Initial load (អាចទុករว่าง ឬទាញយកទាំងអស់សិន មុនពេល User ជ្រើសរើស Group)
    students = UserProfile.query.join(UserType).filter(UserType.TypeName == 'Student').all()
    form.UserID.choices = [(u.ProfileID, u.Name) for u in students]

    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.SubjectID.choices = [(s.SubjectID, s.Name) for s in Subject.query.all()]

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if form.validate_on_submit():
        latest_qr = QrCode.query.order_by(QrCode.QrCodeID.desc()).first()
        qr_id = latest_qr.QrCodeID if latest_qr else 1

        attendance = Attendance(
            ProfileID=form.UserID.data,
            QrCodeID=qr_id,
            ScanNumber=form.Code.data,
            Status=form.Status.data,
            GroupID=form.GroupID.data,
            SubjectID=form.SubjectID.data,
            Date=datetime.combine(form.Date.data, form.Time.data),
            Remarks=form.Remarks.data if hasattr(form, 'Remarks') else None
        )
        db.session.add(attendance)
        db.session.commit()
        flash('Attendance recorded successfully!', 'success')
        return redirect(url_for('attendance.manage_attendances'))

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Validation Error [{field}]: {error}', 'danger')

    pagination = Attendance.query.paginate(page=page, per_page=per_page, error_out=False)
    attendances = pagination.items

    return render_template(
        'attendance/attendances.html',
        form=form,
        attendances=attendances,
        pagination=pagination
    )


# 4. Edit Attendance Route
@attendance_bp.route('/records/edit/<int:id>', methods=['POST'])
def edit_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    form = AttendanceForm()

    students = UserProfile.query.join(UserType).filter(UserType.TypeName == 'Student').all()
    form.UserID.choices = [(u.ProfileID, u.Name) for u in students]

    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.SubjectID.choices = [(s.SubjectID, s.Name) for s in Subject.query.all()]

    if form.validate_on_submit():
        attendance.ProfileID = form.UserID.data
        attendance.ScanNumber = form.Code.data
        attendance.Status = form.Status.data
        attendance.GroupID = form.GroupID.data
        attendance.SubjectID = form.SubjectID.data
        attendance.Date = datetime.combine(form.Date.data, form.Time.data)
        if hasattr(attendance, 'Remarks'):
            attendance.Remarks = form.Remarks.data

        db.session.commit()
        flash('Attendance updated successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Edit Validation Error [{field}]: {error}', 'danger')

    return redirect(url_for('attendance.manage_attendances'))


# 5. Delete Attendance Route
@attendance_bp.route('/records/delete/<int:id>', methods=['POST'])
def delete_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    db.session.delete(attendance)
    db.session.commit()
    flash('Attendance deleted successfully!', 'success')
    return redirect(url_for('attendance.manage_attendances'))


# 6. Active QR Code Sessions Listing Route for Scanning
@attendance_bp.route('/scan/active', methods=['GET'])
@login_required
def active_scan_sessions():
    now = datetime.now()
    active_qrs = QrCode.query.filter(QrCode.StartDate <= now, QrCode.EndDate >= now).all()
    return render_template('attendance/active_scans.html', active_qrs=active_qrs)


# 7. QR Code Scanning Route (Requires Login & uses specific qrid)
@attendance_bp.route('/scan/<int:qrid>', methods=['GET', 'POST'])
@login_required
def scan_attendance(qrid):
    qr = QrCode.query.get_or_404(qrid)
    now = datetime.now()

    if not (qr.StartDate <= now <= qr.EndDate):
        flash('This QR code session has expired or is not yet active for scanning.', 'danger')
        return render_template('attendance/scan.html', qr=qr, status='expired')

    user_profile_id = getattr(current_user, 'ProfileID', getattr(current_user, 'id', None))

    existing_attendance = Attendance.query.filter_by(
        ProfileID=user_profile_id,
        QrCodeID=qr.QrCodeID
    ).first()

    if existing_attendance:
        flash('You have already recorded your attendance for this session!', 'warning')
        return render_template('attendance/scan.html', qr=qr, status='already_recorded')

    try:
        attendance = Attendance(
            ProfileID=user_profile_id,
            QrCodeID=qr.QrCodeID,
            ScanNumber=f'QR-SCAN-{qr.QrCodeID}',
            Status='Present',
            GroupID=qr.session.GroupID if hasattr(qr, 'session') and qr.session else None,
            SubjectID=qr.SubjectID,
            Date=datetime.now(),
            Remarks='Scanned via QR Code'
        )
        db.session.add(attendance)
        db.session.commit()

        flash('Attendance recorded successfully!', 'success')
        return render_template('attendance/scan.html', qr=qr, status='success')

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while recording attendance: {e}', 'danger')
        return render_template('attendance/scan.html', qr=qr)