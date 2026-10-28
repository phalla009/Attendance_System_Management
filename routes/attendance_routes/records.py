from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from forms.attendance_form import AttendanceForm
from models.academic import Group, Subject
from models.attendance import Attendance, QrCode
from models.user import UserProfile, UserType
from . import attendance_bp


@attendance_bp.route('/records', methods=['GET', 'POST'])
@login_required
def manage_attendances():
    form = AttendanceForm()

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


@attendance_bp.route('/records/edit/<int:id>', methods=['POST'])
@login_required
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


@attendance_bp.route('/records/delete/<int:id>', methods=['POST'])
@login_required
def delete_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    db.session.delete(attendance)
    db.session.commit()
    flash('Attendance deleted successfully!', 'success')
    return redirect(url_for('attendance.manage_attendances'))


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