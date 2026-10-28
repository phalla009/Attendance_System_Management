from datetime import datetime
from flask import flash, jsonify, redirect, render_template, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired
from extensions import db
from models.academic import Class, Group, Session, Subject
from models.attendance import QrCode
from models.user import UserProfile, UserType
from . import attendance_bp


class QrCodeForm(FlaskForm):
    SessionID = SelectField('Session', coerce=int, validators=[DataRequired()])
    ClassID = SelectField('Class', coerce=int, validators=[DataRequired()])
    GroupID = SelectField('Group', coerce=int, validators=[DataRequired()])
    SubjectID = SelectField('Subject', coerce=int, validators=[DataRequired()])
    StartDate = StringField('Start Date & Time', validators=[DataRequired()])
    EndDate = StringField('End Date & Time', validators=[DataRequired()])


@attendance_bp.route('/qrcodes', methods=['GET', 'POST'])
@login_required
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


@attendance_bp.route('/qrcodes/edit/<int:id>', methods=['POST'])
@login_required
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
@login_required
def delete_qrcode(id):
    qr = QrCode.query.get_or_404(id)
    try:
        db.session.delete(qr)
        db.session.commit()
        flash('QR Code session deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this QR Code because it is linked to attendance records!', 'danger')

    return redirect(url_for('attendance.manage_qrcodes'))


@attendance_bp.route('/api/students/<int:group_id>', methods=['GET'])
@login_required
def get_students_by_group(group_id):
    students = UserProfile.query.join(UserType).filter(
        UserType.TypeName == 'Student',
        UserProfile.GroupID == group_id
    ).all()

    result = [{'ProfileID': u.ProfileID, 'Name': u.Name} for u in students]
    return jsonify(result)