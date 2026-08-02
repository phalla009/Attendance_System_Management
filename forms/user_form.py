from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import DateField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, Length, Optional


class LoginForm(FlaskForm):
  Username = StringField('Username', validators=[DataRequired(), Length(max=50)])
  Password = StringField('Password', validators=[DataRequired(), Length(max=100)])


class UserTypeForm(FlaskForm):
  Code = StringField('Code', validators=[DataRequired(), Length(max=20)])
  TypeName = StringField(
      'Type Name', validators=[DataRequired(), Length(max=50)]
  )


class ContactNoForm(FlaskForm):
  ContactNumber = StringField(
      'Contact Number', validators=[DataRequired(), Length(max=20)]
  )


class AddressForm(FlaskForm):
  Home = StringField('Home', validators=[Length(max=50)])
  Street = StringField('Street', validators=[Length(max=100)])
  ProvinceID = SelectField(
      'Province', coerce=int, validators=[DataRequired()]
  )
  DistrictID = SelectField(
      'District', coerce=int, validators=[DataRequired()]
  )
  CommuneID = SelectField('Commune', coerce=int, validators=[DataRequired()])
  VillageID = SelectField('Village', coerce=int, validators=[DataRequired()])


class UserProfileForm(FlaskForm):
  Code = StringField('Code', validators=[DataRequired(), Length(max=50)])
  Name = StringField('Name', validators=[DataRequired(), Length(max=100)])
  DOB = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])

  Photo = FileField('Photo', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])

  TypeID = SelectField('User Type', coerce=int, validators=[DataRequired()])
  GroupID = SelectField('Group', coerce=int, validators=[DataRequired()])
  ClassID = SelectField('Class', coerce=int, validators=[DataRequired()])
  SubjectID = SelectField('Subject', coerce=int, validators=[DataRequired()])
  AddressID = SelectField('Address', coerce=int, validators=[DataRequired()])
  ContactNoID = SelectField(
    'Contact No', coerce=int, validators=[DataRequired()]
  )