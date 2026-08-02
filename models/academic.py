from extensions import db

class Session(db.Model):
  __tablename__ = 'sessions'
  SessionID = db.Column(db.Integer, primary_key=True)
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Session_name = db.Column(db.String(100), nullable=False)

class Class(db.Model):
  __tablename__ = 'classes'
  ClassID = db.Column(db.Integer, primary_key=True)
  SessionID = db.Column(db.Integer, db.ForeignKey('sessions.SessionID'))
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Name = db.Column(db.String(100), nullable=False)

class Group(db.Model):
  __tablename__ = 'groups'
  GroupID = db.Column(db.Integer, primary_key=True)
  SessionID = db.Column(db.Integer, db.ForeignKey('sessions.SessionID'))
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Name = db.Column(db.String(100), nullable=False)
  ScheduleID = db.Column(db.Integer)

class Subject(db.Model):
  __tablename__ = 'subjects'
  SubjectID = db.Column(db.Integer, primary_key=True)
  GroupID = db.Column(db.Integer, db.ForeignKey('groups.GroupID'))
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Name = db.Column(db.String(100), nullable=False)