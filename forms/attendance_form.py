from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, TimeField
from wtforms.validators import DataRequired, Length




class AttendanceForm(FlaskForm):
    Code = StringField('Code', validators=[DataRequired(), Length(max=50)])
    Name = StringField('Name',validators=[Length(max=100)])
    GroupID = SelectField('Group', coerce=int)
    UserID = SelectField('User / Student', coerce=int, validators=[DataRequired()])
    SubjectID = SelectField('Subject', coerce=int, validators=[DataRequired()])
    Date = DateField('Attendance Date', validators=[DataRequired()])
    Time = TimeField('Attendance Time', validators=[DataRequired()])
    Status = SelectField(
        'Status',
        choices=[
            ('Present', 'Present (វត្តមាន)'),
            ('Late', 'Late (យឺត)'),
            ('Absent', 'Absent (អវត្តមាន)'),
            ('Permission', 'Permission (ច្បាប់)'),
        ],
        validators=[DataRequired()],
    )
    Remarks = StringField('Remarks', validators=[Length(max=255)])