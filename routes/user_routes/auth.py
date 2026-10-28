from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user
from models.user import ContactNo, UserProfile
from . import user_bp


@user_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_name = request.form.get('username')
        entered_phone = request.form.get('password')

        profile = UserProfile.query.filter(
            UserProfile.Name.ilike(f"%{entered_name}%")
        ).first()

        is_valid = False
        if profile and profile.ContactNoID:
            contact_record = ContactNo.query.get(profile.ContactNoID)
            if contact_record and contact_record.ContactNumber == entered_phone:
                is_valid = True

        if is_valid:
            login_user(profile)

            user_type_name = (
                profile.user_type.TypeName if profile.user_type else "Student"
            )

            session['user_id'] = profile.ProfileID
            session['username'] = profile.Name
            session['user_type'] = user_type_name

            flash(
                f'Logged in successfully as {profile.Name} ({user_type_name})!',
                'success',
            )
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Student Name or Contact Number!', 'danger')

    return render_template('users/login.html')


@user_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.login'))