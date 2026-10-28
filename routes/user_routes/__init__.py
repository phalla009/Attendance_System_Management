from flask import Blueprint
from models.academic import Group, Subject
from models.location import Address
from models.user import ContactNo, UserType

user_bp = Blueprint('user', __name__, url_prefix='/users')


# 👉 Helper function សម្រាប់ Student Choices
def populate_student_form_choices(form):
    form.TypeID.choices = [(t.TypeID, t.TypeName) for t in UserType.query.all()]
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.AddressID.choices = [
        (a.AddressID, f"ផ្ទះលេខ {a.Home or ''}, ផ្លូវ {a.Street or ''}")
        for a in Address.query.all()
    ]
    form.ContactNoID.choices = [
        (c.ContactID, c.ContactNumber) for c in ContactNo.query.all()
    ]


# 👉 Helper function សម្រាប់ Teacher Choices
def populate_teacher_form_choices(form):
    form.TypeID.choices = [(t.TypeID, t.TypeName) for t in UserType.query.all()]
    form.SubjectID.choices = [
        (s.SubjectID, s.Name) for s in Subject.query.all()
    ]
    form.AddressID.choices = [
        (a.AddressID, f"ផ្ទះលេខ {a.Home or ''}, ផ្លូវ {a.Street or ''}")
        for a in Address.query.all()
    ]
    form.ContactNoID.choices = [
        (c.ContactID, c.ContactNumber) for c in ContactNo.query.all()
    ]


# Import views ទាំងអស់ចូលក្នុង Blueprint
from . import addresses, auth, contacts, dashboard, profiles, usertypes