from extensions import db

class ContactNo(db.Model):
  __tablename__ = 'contact_nos'
  ContactID = db.Column(db.Integer, primary_key=True)
  Email = db.Column(db.String(120))
  ContactNumber = db.Column(db.String(50))

class UserType(db.Model):
  __tablename__ = 'user_types'
  TypeID = db.Column(db.Integer, primary_key=True)
  Code = db.Column(db.String(50), unique=True, nullable=False)
  TypeName = db.Column(db.String(100), nullable=False)

class UserProfile(db.Model):
  __tablename__ = 'user_profiles'
  ProfileID = db.Column(db.Integer, primary_key=True)
  AddressID = db.Column(db.Integer, db.ForeignKey('addresses.AddressID'))
  GroupID = db.Column(db.Integer, db.ForeignKey('groups.GroupID'))
  ClassID = db.Column(db.Integer, db.ForeignKey('classes.ClassID'))
  TypeID = db.Column(db.Integer, db.ForeignKey('user_types.TypeID'))
  ContactNoID = db.Column(db.Integer, db.ForeignKey('contact_nos.ContactID'))
  SubjectID = db.Column(db.Integer, db.ForeignKey('subjects.SubjectID'))
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Name = db.Column(db.String(150), nullable=False)
  Gender = db.Column(db.String(10), nullable=True)
  DOB = db.Column(db.Date)
  Photo = db.Column(db.String(255))

  user_type = db.relationship('UserType')
  class_rel = db.relationship('Class')
  group_rel = db.relationship('Group')
  subject_rel = db.relationship('Subject')
  address_rel = db.relationship('Address')
  contact_rel = db.relationship('ContactNo')

class Login(db.Model):
  __tablename__ = 'logins'
  LoginID = db.Column(db.Integer, primary_key=True)
  ProfileID = db.Column(
      db.Integer,
      db.ForeignKey('user_profiles.ProfileID'),
      unique=True,
      nullable=False,
  )
  Full_name = db.Column(db.String(150), nullable=False)
  Password = db.Column(db.String(255), nullable=False)