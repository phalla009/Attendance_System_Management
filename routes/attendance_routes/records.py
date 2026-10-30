from datetime import datetime, timedelta
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import extract, or_
from extensions import db
from forms.attendance_form import AttendanceForm
from models.academic import Class, Group, Session, Subject
from models.attendance import Attendance, QrCode
from models.user import UserProfile, UserType
from . import attendance_bp

VALID_STATUSES = ('Present', 'Late', 'Absent', 'Permission')


def student_group_ids(u):
    """Return the list of GroupIDs a student belongs to.

    Supports both a many-to-many relationship (u.groups)
    and a single column (u.GroupID). Adjust here if your model differs.
    """
    if hasattr(u, 'groups'):
        return [g.GroupID for g in u.groups]
    gid = getattr(u, 'GroupID', None)
    return [gid] if gid is not None else []


def all_students():
    return UserProfile.query.join(UserType).filter(UserType.TypeName == 'Student').all()


def parse_time(value):
    """Parse 'HH:MM' (or 'HH:MM:SS') from a time input. Returns a time or None."""
    if not value:
        return None
    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


@attendance_bp.route('/records', methods=['GET', 'POST'])
@login_required
def manage_attendances():
    form = AttendanceForm()

    students = all_students()
    form.UserID.choices = [(u.ProfileID, u.Name) for u in students]
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.SubjectID.choices = [(s.SubjectID, s.Name) for s in Subject.query.all()]

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filters from the dropdowns / inputs (GET)
    session_id = request.args.get('session_id', type=int)
    class_id = request.args.get('class_id', type=int)
    group_id = request.args.get('group_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    date_str = request.args.get('date', '', type=str)
    time_from_str = request.args.get('time_from', '', type=str)
    time_to_str = request.args.get('time_to', '', type=str)

    sessions = Session.query.order_by(Session.Session_name).all()

    classes_q = Class.query
    groups_q = Group.query
    if session_id:
        classes_q = classes_q.filter(Class.SessionID == session_id)
        groups_q = groups_q.filter(Group.ScheduleID == session_id)

    # ប្រសិនបើមានការជ្រើសរើស Class អាចទាញយក SessionID របស់ Class មកជួយ Filter Group បន្ថែម
    if class_id:
        selected_class = Class.query.get(class_id)
        if selected_class and selected_class.SessionID:
            groups_q = groups_q.filter(Group.ScheduleID == selected_class.SessionID)

    classes = classes_q.order_by(Class.Name).all()
    groups = groups_q.order_by(Group.Name).all()

    # Drop selections that don't belong to the chosen session
    if class_id and class_id not in [c.ClassID for c in classes]:
        class_id = None
    if group_id and group_id not in [g.GroupID for g in groups]:
        group_id = None

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
        return redirect(url_for('attendance.manage_attendances', session_id=session_id,
                                class_id=class_id, group_id=group_id, subject_id=subject_id,
                                date=date_str or None,
                                time_from=time_from_str or None,
                                time_to=time_to_str or None))

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Validation Error [{field}]: {error}', 'danger')

    query = Attendance.query

    # Join Group ដើម្បី Filter តាម Session និង Class
    if session_id or class_id:
        query = query.join(Group, Attendance.GroupID == Group.GroupID)
        if session_id:
            query = query.filter(Group.ScheduleID == session_id)
        if class_id:
            # ភ្ជាប់តាមរយៈ SessionID ដែល Class និង Group មានដូចគ្នា
            query = query.join(Class, Group.ScheduleID == Class.SessionID).filter(Class.ClassID == class_id)

    if group_id:
        query = query.filter(Attendance.GroupID == group_id)
    if subject_id:
        query = query.filter(Attendance.SubjectID == subject_id)

    # Date filter: the whole selected day
    if date_str:
        try:
            day_start = datetime.strptime(date_str, '%Y-%m-%d')
            query = query.filter(Attendance.Date >= day_start,
                                 Attendance.Date < day_start + timedelta(days=1))
        except ValueError:
            date_str = ''

    # Time-of-day range filter: from HH:MM to HH:MM (inclusive, by minute).
    t_from = parse_time(time_from_str)
    t_to = parse_time(time_to_str)
    if not t_from:
        time_from_str = ''
    if not t_to:
        time_to_str = ''

    if t_from or t_to:
        minutes = (extract('hour', Attendance.Date) * 60
                   + extract('minute', Attendance.Date))
        from_min = t_from.hour * 60 + t_from.minute if t_from else None
        to_min = t_to.hour * 60 + t_to.minute if t_to else None

        if from_min is not None and to_min is not None:
            if from_min <= to_min:
                query = query.filter(minutes >= from_min, minutes <= to_min)
            else:
                query = query.filter(or_(minutes >= from_min, minutes <= to_min))
        elif from_min is not None:
            query = query.filter(minutes >= from_min)
        else:
            query = query.filter(minutes <= to_min)

    pagination = query.order_by(Attendance.Date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    attendances = pagination.items

    # Data used by the template to filter Students by the selected Group
    students_data = [
        {'id': u.ProfileID, 'name': u.Name, 'groups': student_group_ids(u)}
        for u in students
    ]

    return render_template(
        'attendance/attendances.html',
        form=form,
        attendances=attendances,
        pagination=pagination,
        students_data=students_data,
        sessions=sessions,
        classes=classes,
        groups=groups,
        subjects=Subject.query.order_by(Subject.Name).all(),
        session_id=session_id,
        class_id=class_id,
        group_id=group_id,
        subject_id=subject_id,
        date_str=date_str,
        time_from_str=time_from_str,
        time_to_str=time_to_str,
    )


@attendance_bp.route('/records/take', methods=['GET', 'POST'])
@login_required
def take_attendance():
    """Pick Session -> Class / Group + Subject + Date, list that group's students,
    and save (or edit) everyone's attendance in one go."""
    form = AttendanceForm()

    src = request.form if request.method == 'POST' else request.args
    session_id = src.get('session_id', type=int)
    class_id = src.get('class_id', type=int)
    group_id = src.get('group_id', type=int)
    subject_id = src.get('subject_id', type=int)
    date_str = src.get('date') or datetime.now().strftime('%Y-%m-%d')
    time_str = src.get('time') or datetime.now().strftime('%H:%M')

    sessions = Session.query.order_by(Session.Session_name).all()
    classes_q = Class.query
    groups_q = Group.query
    if session_id:
        classes_q = classes_q.filter(Class.SessionID == session_id)
        groups_q = groups_q.filter(Group.ScheduleID == session_id)
    classes = classes_q.order_by(Class.Name).all()
    groups = groups_q.order_by(Group.Name).all()
    subjects = Subject.query.order_by(Subject.Name).all()

    if class_id and class_id not in [c.ClassID for c in classes]:
        class_id = None
    if group_id and group_id not in [g.GroupID for g in groups]:
        group_id = None

    try:
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        att_time = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        flash('Invalid date or time.', 'danger')
        return redirect(url_for('attendance.take_attendance'))

    students = []
    existing = {}
    if group_id:
        students = sorted(
            [s for s in all_students() if group_id in student_group_ids(s)],
            key=lambda s: s.Name or ''
        )

        if subject_id:
            day_start = datetime.combine(att_date, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            existing = {
                a.ProfileID: a
                for a in Attendance.query.filter(
                    Attendance.GroupID == group_id,
                    Attendance.SubjectID == subject_id,
                    Attendance.Date >= day_start,
                    Attendance.Date < day_end,
                ).all()
            }

    if request.method == 'POST':
        if not (group_id and subject_id):
            flash('Please select a group and a subject first.', 'danger')
            return redirect(url_for('attendance.take_attendance', session_id=session_id,
                                    class_id=class_id))

        latest_qr = QrCode.query.order_by(QrCode.QrCodeID.desc()).first()
        qr_id = latest_qr.QrCodeID if latest_qr else 1
        when = datetime.combine(att_date, att_time)

        created = updated = 0
        for s in students:
            status = request.form.get(f'status_{s.ProfileID}')
            if status not in VALID_STATUSES:
                continue
            remarks = (request.form.get(f'remarks_{s.ProfileID}') or '').strip() or None

            record = existing.get(s.ProfileID)
            if record:
                record.Status = status
                record.Remarks = remarks
                record.Date = when
                updated += 1
            else:
                db.session.add(Attendance(
                    ProfileID=s.ProfileID,
                    QrCodeID=qr_id,
                    ScanNumber=s.Code,
                    Status=status,
                    GroupID=group_id,
                    SubjectID=subject_id,
                    Date=when,
                    Remarks=remarks,
                ))
                created += 1

        try:
            db.session.commit()
            flash(f'Attendance saved: {created} added, {updated} updated.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Could not save attendance: {e}', 'danger')

        return redirect(url_for('attendance.take_attendance', session_id=session_id,
                                class_id=class_id, group_id=group_id,
                                subject_id=subject_id, date=date_str, time=time_str))

    current_session = next((s for s in sessions if s.SessionID == session_id), None)
    current_class = next((c for c in classes if c.ClassID == class_id), None)
    current_group = next((g for g in groups if g.GroupID == group_id), None)
    current_subject = next((s for s in subjects if s.SubjectID == subject_id), None)

    return render_template(
        'attendance/take_attendance.html',
        form=form,
        sessions=sessions,
        classes=classes,
        groups=groups,
        subjects=subjects,
        students=students,
        existing=existing,
        session_id=session_id,
        class_id=class_id,
        group_id=group_id,
        subject_id=subject_id,
        current_session=current_session,
        current_class=current_class,
        current_group=current_group,
        current_subject=current_subject,
        date_str=date_str,
        time_str=time_str,
    )


@attendance_bp.route('/records/edit/<int:id>', methods=['POST'])
@login_required
def edit_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    form = AttendanceForm()

    students = all_students()
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