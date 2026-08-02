from datetime import datetime
from extensions import db

class QrCode(db.Model):
    __tablename__ = 'qr_codes'
    QrCodeID = db.Column(db.Integer, primary_key=True)
    SessionID = db.Column(db.Integer, db.ForeignKey('sessions.SessionID'))
    SubjectID = db.Column(db.Integer, db.ForeignKey('subjects.SubjectID'), nullable=False)
    StartDate = db.Column(db.DateTime, nullable=False)
    EndDate = db.Column(db.DateTime, nullable=False)
    session = db.relationship('Session', backref='qrcodes')
    subject = db.relationship('Subject', backref='qrcodes')

class Attendance(db.Model):
    __tablename__ = 'attendances'
    AttendanceID = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    ProfileID = db.Column(
        db.Integer, db.ForeignKey('user_profiles.ProfileID'), nullable=False
    )
    QrCodeID = db.Column(
        db.Integer, db.ForeignKey('qr_codes.QrCodeID'), nullable=False
    )
    SubjectID = db.Column(
        db.Integer, db.ForeignKey('subjects.SubjectID'), nullable=True
    )
    GroupID = db.Column(
        db.Integer, db.ForeignKey('groups.GroupID'), nullable=True
    )

    # Fields
    ScanNumber = db.Column(db.String(50))
    Date = db.Column(db.DateTime, default=datetime.utcnow)
    Status = db.Column(db.String(50), default='Present')
    Remarks = db.Column(db.String(255), nullable=True)

    # Relationships
    user = db.relationship('UserProfile', backref=db.backref('attendances', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('attendances', lazy=True))
    group = db.relationship('Group', backref=db.backref('attendances', lazy=True))