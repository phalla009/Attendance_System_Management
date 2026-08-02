from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, Length


class ProvinceForm(FlaskForm):
  Code = StringField('Code', validators=[DataRequired(), Length(max=50)])
  Name = StringField('Name', validators=[DataRequired(), Length(max=100)])


class DistrictForm(FlaskForm):
  ProvinceID = SelectField(
      'Province', coerce=int, validators=[DataRequired()]
  )
  Code = StringField('Code', validators=[DataRequired(), Length(max=50)])
  Name = StringField('Name', validators=[DataRequired(), Length(max=100)])


class CommuneForm(FlaskForm):
  DistrictID = SelectField(
      'District', coerce=int, validators=[DataRequired()]
  )
  Code = StringField('Code', validators=[DataRequired(), Length(max=50)])
  Name = StringField('Name', validators=[DataRequired(), Length(max=100)])


class VillageForm(FlaskForm):
  CommuneID = SelectField('Commune', coerce=int, validators=[DataRequired()])
  Code = StringField('Code', validators=[DataRequired(), Length(max=50)])
  Name = StringField('Name', validators=[DataRequired(), Length(max=100)])


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