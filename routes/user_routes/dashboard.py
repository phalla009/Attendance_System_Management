from flask import render_template
from flask_login import login_required
from models.location import Address
from models.user import ContactNo, UserProfile, UserType
from . import user_bp


@user_bp.route('/dashboard', methods=['GET'])
@login_required
def users_dashboard():
    total_profiles = UserProfile.query.count()
    total_usertypes = UserType.query.count()
    total_contacts = ContactNo.query.count()
    total_addresses = Address.query.count()

    total_teachers = UserProfile.query.filter_by(TypeID=1).count()
    total_students = UserProfile.query.filter_by(TypeID=2).count()

    return render_template(
        'users/dashboard.html',
        total_profiles=total_profiles,
        total_usertypes=total_usertypes,
        total_contacts=total_contacts,
        total_addresses=total_addresses,
        total_teachers=total_teachers,
        total_students=total_students,
    )