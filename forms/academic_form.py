from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from models.academic import Session, Class, Group, Subject


class SessionForm(FlaskForm):
    Code = StringField('Session Code', validators=[DataRequired(), Length(max=50)])
    Session_name = StringField('Session Name', validators=[DataRequired(), Length(max=100)])

    def validate_Code(self, field):
        session_id = getattr(self, '_session_id', None)
        query = Session.query.filter_by(Code=field.data)
        if session_id:
            query = query.filter(Session.SessionID != session_id)

        if query.first():
            raise ValidationError('This Session Code already exists. Please use a different code.')


class ClassForm(FlaskForm):
    Code = StringField('Class Code', validators=[DataRequired(), Length(max=50)])
    Name = StringField('Class Name', validators=[DataRequired(), Length(max=100)])
    SessionID = SelectField('Session', coerce=int, validators=[DataRequired()])

    def validate_Code(self, field):
        class_id = getattr(self, '_class_id', None)
        query = Class.query.filter_by(Code=field.data)
        if class_id:
            query = query.filter(Class.ClassID != class_id)

        if query.first():
            raise ValidationError('This Class Code already exists. Please use a different code.')


class GroupForm(FlaskForm):
    Code = StringField('Group Code', validators=[DataRequired(), Length(max=50)])
    Name = StringField('Group Name', validators=[DataRequired(), Length(max=100)])
    # Dropdown ជ្រើសរើស Session (0 = គ្មាន Session)
    ScheduleID = SelectField('Session', coerce=int, validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ScheduleID.choices = [(0, '-- Select Session --')] + [
            (s.SessionID, f'{s.Session_name} ({s.Code})')
            for s in Session.query.order_by(Session.Session_name).all()
        ]

    def validate_Code(self, field):
        group_id = getattr(self, '_group_id', None)
        query = Group.query.filter_by(Code=field.data)
        if group_id:
            query = query.filter(Group.GroupID != group_id)

        if query.first():
            raise ValidationError('This Group Code already exists. Please use a different code.')


class SubjectForm(FlaskForm):
    Code = StringField('Subject Code', validators=[DataRequired(), Length(max=50)])
    Name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])

    def validate_Code(self, field):
        subject_id = getattr(self, '_subject_id', None)
        query = Subject.query.filter_by(Code=field.data)
        if subject_id:
            query = query.filter(Subject.SubjectID != subject_id)

        if query.first():
            raise ValidationError('This Subject Code already exists. Please use a different code.')