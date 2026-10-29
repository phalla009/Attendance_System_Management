from flask import Blueprint
from models.academic import Group, Subject
from models.user import ContactNo, UserType

user_bp = Blueprint('user', __name__, url_prefix='/users')


def get_contact_choices():
    return [(c.ContactID, c.ContactNumber) for c in ContactNo.query.all()]


# 👉 Helper function សម្រាប់ Student Choices
# (Address មិនប្រើ dropdown ទៀតទេ: ជ្រើសខេត្ត/ស្រុក/ឃុំ/ភូមិ ដោយ cascade ក្នុង template)
def populate_student_form_choices(form):
    form.TypeID.choices = [(t.TypeID, t.TypeName) for t in UserType.query.all()]
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.ContactNoID.choices = get_contact_choices()


# 👉 Helper function សម្រាប់ Teacher Choices
def populate_teacher_form_choices(form):
    form.TypeID.choices = [(t.TypeID, t.TypeName) for t in UserType.query.all()]
    form.SubjectID.choices = [
        (s.SubjectID, s.Name) for s in Subject.query.all()
    ]
    form.ContactNoID.choices = get_contact_choices()


# Import views ទាំងអស់ចូលក្នុង Blueprint
from . import addresses, auth, contacts, dashboard, profiles, usertypes