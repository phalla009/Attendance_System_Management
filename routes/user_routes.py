import os
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
from extensions import db
from forms.user_form import (
    AddressForm,
    ContactNoForm,
    UserProfileForm,
    UserTypeForm,
)
from models.academic import Class, Group, Subject
from models.location import Address, Province, District, Commune, Village
from models.user import ContactNo, Login, UserProfile, UserType

user_bp = Blueprint('user', __name__, url_prefix='/users')

# 👉 Route for Login
@user_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_name = request.form.get('username')
        entered_phone = request.form.get('password')

        profile = UserProfile.query.filter(UserProfile.Name.ilike(f"%{entered_name}%")).first()

        is_valid = False
        if profile and profile.ContactNoID:
            contact_record = ContactNo.query.get(profile.ContactNoID)
            if contact_record and contact_record.ContactNumber == entered_phone:
                is_valid = True

        if is_valid:
            user_type_name = profile.user_type.TypeName if profile.user_type else "Student"

            session['user_id'] = profile.ProfileID
            session['username'] = profile.Name
            session['user_type'] = user_type_name

            flash(f'Logged in successfully as {profile.Name} ({user_type_name})!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Student Name or Contact Number!', 'danger')

    return render_template('users/login.html')

# 👉 Route for Logout
@user_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.login'))

# ----------------- PROFILES -----------------
@user_bp.route('/profiles', methods=['GET', 'POST'])
def manage_profiles():
    form = UserProfileForm()
    form.TypeID.choices = [(t.TypeID, t.TypeName) for t in UserType.query.all()]
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.ClassID.choices = [(c.ClassID, c.Name) for c in Class.query.all()]
    form.SubjectID.choices = [(s.SubjectID, s.Name) for s in Subject.query.all()]

    form.AddressID.choices = [
        (a.AddressID, f"ផ្ទះលេខ {a.Home or ''}, ផ្លូវ {a.Street or ''}")
        for a in Address.query.all()
    ]
    form.ContactNoID.choices = [
        (c.ContactID, c.ContactNumber) for c in ContactNo.query.all()
    ]

    if request.method == 'POST':
        if session.get('user_type') != 'Teacher':
            flash('Access Denied! Only Teacher can add user profiles.', 'danger')
            return redirect(url_for('user.manage_profiles'))

        if form.validate_on_submit():
            photo_filename = None
            if form.Photo.data:
                photo_file = form.Photo.data
                filename = secure_filename(photo_file.filename)
                if filename:
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                    os.makedirs(upload_folder, exist_ok=True)

                    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    photo_filename = f"{uuid.uuid4().hex}.{ext}"
                    photo_file.save(os.path.join(upload_folder, photo_filename))

            user = UserProfile(
                Code=form.Code.data,
                Name=form.Name.data,
                DOB=form.DOB.data,
                Photo=photo_filename,
                TypeID=form.TypeID.data,
                GroupID=form.GroupID.data,
                ClassID=form.ClassID.data,
                SubjectID=form.SubjectID.data,
                AddressID=form.AddressID.data,
                ContactNoID=form.ContactNoID.data,
            )
            db.session.add(user)
            db.session.commit()
            flash('User Profile added successfully!', 'success')
            return redirect(url_for('user.manage_profiles'))

    profiles = UserProfile.query.all()
    return render_template('users/profiles.html', form=form, profiles=profiles)

@user_bp.route('/profiles/edit/<int:id>', methods=['POST'])
def edit_profile(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can edit user profiles.', 'danger')
        return redirect(url_for('user.manage_profiles'))

    user = UserProfile.query.get_or_404(id)
    form = UserProfileForm()

    form.TypeID.choices = [(t.TypeID, t.TypeName) for t in UserType.query.all()]
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.ClassID.choices = [(c.ClassID, c.Name) for c in Class.query.all()]
    form.SubjectID.choices = [(s.SubjectID, s.Name) for s in Subject.query.all()]
    form.AddressID.choices = [
        (a.AddressID, f"ផ្ទះលេខ {a.Home or ''}, ផ្លូវ {a.Street or ''}")
        for a in Address.query.all()
    ]
    form.ContactNoID.choices = [
        (c.ContactID, c.ContactNumber) for c in ContactNo.query.all()
    ]

    if form.validate_on_submit():
        user.Name = form.Name.data
        user.DOB = form.DOB.data
        user.TypeID = form.TypeID.data
        user.GroupID = form.GroupID.data
        user.ClassID = form.ClassID.data
        user.SubjectID = form.SubjectID.data
        user.AddressID = form.AddressID.data
        user.ContactNoID = form.ContactNoID.data

        if form.Photo.data:
            photo_file = form.Photo.data
            filename = secure_filename(photo_file.filename)
            if filename:
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                os.makedirs(upload_folder, exist_ok=True)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                photo_filename = f"{uuid.uuid4().hex}.{ext}"
                photo_file.save(os.path.join(upload_folder, photo_filename))
                user.Photo = photo_filename

        db.session.commit()
        flash('User Profile updated successfully!', 'success')
        return redirect(url_for('user.manage_profiles'))

    profiles = UserProfile.query.all()
    flash('Failed to update profile. Please check your inputs.', 'danger')
    return render_template('users/profiles.html', form=form, profiles=profiles, edit_error_id=id)

@user_bp.route('/profiles/delete/<int:id>', methods=['POST'])
def delete_profile(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can delete user profiles.', 'danger')
        return redirect(url_for('user.manage_profiles'))

    user = UserProfile.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User Profile deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this profile because it is linked to other records!', 'danger')

    return redirect(url_for('user.manage_profiles'))

# ----------------- USER TYPES -----------------
@user_bp.route('/usertypes', methods=['GET', 'POST'])
def manage_usertypes():
    form = UserTypeForm()
    if request.method == 'POST':
        if session.get('user_type') != 'Admin':
            flash('Access Denied! Only Admin can add user types.', 'danger')
            return redirect(url_for('user.manage_usertypes'))

        if form.validate_on_submit():
            usertype = UserType(Code=form.Code.data, TypeName=form.TypeName.data)
            db.session.add(usertype)
            db.session.commit()
            flash('User Type added successfully!', 'success')
            return redirect(url_for('user.manage_usertypes'))

    usertypes = UserType.query.all()
    return render_template('users/usertypes.html', form=form, usertypes=usertypes)

@user_bp.route('/usertypes/edit/<int:id>', methods=['POST'])
def edit_usertype(id):
    if session.get('user_type') != 'Admin':
        flash('Access Denied! Only Admin can edit user types.', 'danger')
        return redirect(url_for('user.manage_usertypes'))

    usertype = UserType.query.get_or_404(id)
    form = UserTypeForm()

    if form.validate_on_submit():
        usertype.Code = form.Code.data
        usertype.TypeName = form.TypeName.data
        db.session.commit()
        flash('User Type updated successfully!', 'success')
        return redirect(url_for('user.manage_usertypes'))

    usertypes = UserType.query.all()
    flash('Failed to update user type. Please check your inputs.', 'danger')
    return render_template('users/usertypes.html', form=form, usertypes=usertypes, edit_error_id=id)

@user_bp.route('/usertypes/delete/<int:id>', methods=['POST'])
def delete_usertype(id):
    if session.get('user_type') != 'Admin':
        flash('Access Denied! Only Admin can delete user types.', 'danger')
        return redirect(url_for('user.manage_usertypes'))

    usertype = UserType.query.get_or_404(id)
    try:
        db.session.delete(usertype)
        db.session.commit()
        flash('User Type deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this user type because it is linked to other records!', 'danger')

    return redirect(url_for('user.manage_usertypes'))
# ----------------- CONTACTS -----------------
@user_bp.route('/contacts', methods=['GET', 'POST'])
def manage_contacts():
    form = ContactNoForm()
    if request.method == 'POST':
        if session.get('user_type') != 'Teacher':
            flash('Access Denied! Only Teacher can add contacts.', 'danger')
            return redirect(url_for('user.manage_contacts'))

        if form.validate_on_submit():
            contact = ContactNo(ContactNumber=form.ContactNumber.data)
            db.session.add(contact)
            db.session.commit()
            flash('Contact Number added successfully!', 'success')
            return redirect(url_for('user.manage_contacts'))

    contacts = ContactNo.query.all()
    return render_template('users/contacts.html', form=form, contacts=contacts)

@user_bp.route('/contacts/edit/<int:id>', methods=['POST'])
def edit_contact(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can edit contacts.', 'danger')
        return redirect(url_for('user.manage_contacts'))

    contact = ContactNo.query.get_or_404(id)
    form = ContactNoForm()

    if form.validate_on_submit():
        contact.ContactNumber = form.ContactNumber.data
        db.session.commit()
        flash('Contact Number updated successfully!', 'success')
        return redirect(url_for('user.manage_contacts'))

    contacts = ContactNo.query.all()
    flash('Failed to update contact. Please check your inputs.', 'danger')
    return render_template('users/contacts.html', form=form, contacts=contacts, edit_error_id=id)

@user_bp.route('/contacts/delete/<int:id>', methods=['POST'])
def delete_contact(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can delete contacts.', 'danger')
        return redirect(url_for('user.manage_contacts'))

    contact = ContactNo.query.get_or_404(id)
    try:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact Number deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this contact because it is linked to user profiles!', 'danger')

    return redirect(url_for('user.manage_contacts'))

# ----------------- ADDRESSES -----------------
@user_bp.route('/addresses', methods=['GET', 'POST'])
def manage_addresses():
    form = AddressForm()
    form.ProvinceID.choices = [(p.ProvinceID, p.Name) for p in Province.query.all()]
    form.DistrictID.choices = [(d.DistrictID, d.Name) for d in District.query.all()]
    form.CommuneID.choices = [(c.CommuneID, c.Name) for c in Commune.query.all()]
    form.VillageID.choices = [(v.VillageID, v.Name) for v in Village.query.all()]

    if request.method == 'POST':
        if session.get('user_type') != 'Teacher':
            flash('Access Denied! Only Teacher can add addresses.', 'danger')
            return redirect(url_for('user.manage_addresses'))

        if form.validate_on_submit():
            address = Address(
                Home=form.Home.data,
                Street=form.Street.data,
                ProvinceID=form.ProvinceID.data,
                DistrictID=form.DistrictID.data,
                CommuneID=form.CommuneID.data,
                VillageID=form.VillageID.data,
            )
            db.session.add(address)
            db.session.commit()
            flash('Address added successfully!', 'success')
            return redirect(url_for('user.manage_addresses'))

    addresses = Address.query.all()
    return render_template('users/addresses.html', form=form, addresses=addresses)

@user_bp.route('/addresses/edit/<int:id>', methods=['POST'])
def edit_address(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can edit addresses.', 'danger')
        return redirect(url_for('user.manage_addresses'))

    address = Address.query.get_or_404(id)
    form = AddressForm()

    form.ProvinceID.choices = [(p.ProvinceID, p.Name) for p in Province.query.all()]
    form.DistrictID.choices = [(d.DistrictID, d.Name) for d in District.query.all()]
    form.CommuneID.choices = [(c.CommuneID, c.Name) for c in Commune.query.all()]
    form.VillageID.choices = [(v.VillageID, v.Name) for v in Village.query.all()]

    if form.validate_on_submit():
        address.Home = form.Home.data
        address.Street = form.Street.data
        address.ProvinceID = form.ProvinceID.data
        address.DistrictID = form.DistrictID.data
        address.CommuneID = form.CommuneID.data
        address.VillageID = form.VillageID.data

        db.session.commit()
        flash('Address updated successfully!', 'success')
        return redirect(url_for('user.manage_addresses'))

    addresses = Address.query.all()
    flash('Failed to update address. Please check your inputs.', 'danger')
    return render_template('users/addresses.html', form=form, addresses=addresses, edit_error_id=id)

@user_bp.route('/addresses/delete/<int:id>', methods=['POST'])
def delete_address(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can delete addresses.', 'danger')
        return redirect(url_for('user.manage_addresses'))

    address = Address.query.get_or_404(id)
    try:
        db.session.delete(address)
        db.session.commit()
        flash('Address deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this address because it is linked to user profiles!', 'danger')

    return redirect(url_for('user.manage_addresses'))