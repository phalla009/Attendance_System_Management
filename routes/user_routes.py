import os
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
from extensions import db
from forms.user_form import (
    AddressForm,
    ContactNoForm,
    StudentProfileForm,
    TeacherProfileForm,
    UserTypeForm,
)
from models.academic import Class, Group, Subject
from models.location import Address, Province, District, Commune, Village
from models.user import ContactNo, Login, UserProfile, UserType

user_bp = Blueprint('user', __name__, url_prefix='/users')


# 👉 Helper function សម្រាប់ Student Choices
def populate_student_form_choices(form):
    form.TypeID.choices = [(t.TypeID, t.TypeName) for t in UserType.query.all()]
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]
    form.ClassID.choices = [(c.ClassID, c.Name) for c in Class.query.all()]
    form.AddressID.choices = [(a.AddressID, f"ផ្ទះលេខ {a.Home or ''}, ផ្លូវ {a.Street or ''}") for a in
                              Address.query.all()]
    form.ContactNoID.choices = [(c.ContactID, c.ContactNumber) for c in ContactNo.query.all()]


# 👉 Helper function សម្រាប់ Teacher Choices
def populate_teacher_form_choices(form):
    form.TypeID.choices = [(t.TypeID, t.TypeName) for t in UserType.query.all()]
    form.SubjectID.choices = [(s.SubjectID, s.Name) for s in Subject.query.all()]
    form.AddressID.choices = [(a.AddressID, f"ផ្ទះលេខ {a.Home or ''}, ផ្លូវ {a.Street or ''}") for a in
                              Address.query.all()]
    form.ContactNoID.choices = [(c.ContactID, c.ContactNumber) for c in ContactNo.query.all()]


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

# ----------------- USERS DASHBOARD / INDEX -----------------
@user_bp.route('/dashboard', methods=['GET'])
def users_dashboard():
    total_profiles = UserProfile.query.count()
    total_usertypes = UserType.query.count()
    total_contacts = ContactNo.query.count()
    total_addresses = Address.query.count()

    # ➕ រាប់ចំនួន Teacher និង Student ផ្ទាល់ពី TypeID
    total_teachers = UserProfile.query.filter_by(TypeID=1).count()
    print(f">>>> TOTAL TEACHERS FOUND: {total_teachers}")  # បង្ហាញក្នុង Terminal ដើម្បី טេស

    total_students = UserProfile.query.filter_by(TypeID=2).count()
    print(f">>>> TOTAL STUDENTS FOUND: {total_students}")  # បង្ហាញក្នុង Terminal ដើម្បី טេស

    return render_template('users/dashboard.html',
                           total_profiles=total_profiles,
                           total_usertypes=total_usertypes,
                           total_contacts=total_contacts,
                           total_addresses=total_addresses,
                           total_teachers=total_teachers,
                           total_students=total_students)


# ----------------- PROFILES (STUDENTS & TEACHERS) -----------------
@user_bp.route('/profiles', methods=['GET'])
def manage_profiles():
    student_form = StudentProfileForm()
    teacher_form = TeacherProfileForm()

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Populate Choices
    populate_student_form_choices(student_form)
    populate_teacher_form_choices(teacher_form)

    pagination = UserProfile.query.paginate(page=page, per_page=per_page, error_out=False)
    profiles = pagination.items

    prev_url = url_for('user.manage_profiles', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('user.manage_profiles', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('users/profiles.html',
                           student_form=student_form,
                           teacher_form=teacher_form,
                           profiles=profiles,
                           per_page=per_page,
                           prev_url=prev_url,
                           next_url=next_url)


@user_bp.route('/profiles/add-student', methods=['POST'])
def manage_students():
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can add student profiles.', 'danger')
        return redirect(url_for('user.manage_profiles'))

    student_form = StudentProfileForm()
    populate_student_form_choices(student_form)

    student_type = UserType.query.filter_by(TypeName='Student').first()
    if student_type:
        student_form.TypeID.data = student_type.TypeID

    if student_form.validate_on_submit():
        photo_filename = None
        if student_form.Photo.data:
            photo_file = student_form.Photo.data
            filename = secure_filename(photo_file.filename)
            if filename:
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                os.makedirs(upload_folder, exist_ok=True)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                photo_filename = f"{uuid.uuid4().hex}.{ext}"
                photo_file.save(os.path.join(upload_folder, photo_filename))

        user = UserProfile(
            Code=student_form.Code.data,
            Name=student_form.Name.data,
            Gender=student_form.Gender.data,
            DOB=student_form.DOB.data,
            Photo=photo_filename,
            TypeID=student_form.TypeID.data,
            GroupID=student_form.GroupID.data,
            ClassID=student_form.ClassID.data,
            AddressID=student_form.AddressID.data,
            ContactNoID=student_form.ContactNoID.data,
        )
        db.session.add(user)
        db.session.commit()
        flash('Student Profile added successfully!', 'success')
        return redirect(url_for('user.manage_profiles'))

    flash(f'Failed to add student profile: {student_form.errors}', 'danger')
    return redirect(url_for('user.manage_profiles'))


@user_bp.route('/profiles/add-teacher', methods=['POST'])
def manage_teachers():
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can add teacher profiles.', 'danger')
        return redirect(url_for('user.manage_profiles'))

    teacher_form = TeacherProfileForm()
    populate_teacher_form_choices(teacher_form)

    teacher_type = UserType.query.filter_by(TypeName='Teacher').first()
    if teacher_type:
        teacher_form.TypeID.data = teacher_type.TypeID

    if teacher_form.validate_on_submit():
        photo_filename = None
        if teacher_form.Photo.data:
            photo_file = teacher_form.Photo.data
            filename = secure_filename(photo_file.filename)
            if filename:
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                os.makedirs(upload_folder, exist_ok=True)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                photo_filename = f"{uuid.uuid4().hex}.{ext}"
                photo_file.save(os.path.join(upload_folder, photo_filename))

        user = UserProfile(
            Code=teacher_form.Code.data,
            Name=teacher_form.Name.data,
            Gender=teacher_form.Gender.data,
            DOB=teacher_form.DOB.data,
            Photo=photo_filename,
            TypeID=teacher_form.TypeID.data,
            SubjectID=teacher_form.SubjectID.data,
            AddressID=teacher_form.AddressID.data,
            ContactNoID=teacher_form.ContactNoID.data,
        )
        db.session.add(user)
        db.session.commit()
        flash('Teacher Profile added successfully!', 'success')
        return redirect(url_for('user.manage_profiles'))

    flash(f'Failed to add teacher profile: {teacher_form.errors}', 'danger')
    return redirect(url_for('user.manage_profiles'))


@user_bp.route('/profiles/edit/<int:id>', methods=['POST'])
def edit_profile(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can edit user profiles.', 'danger')
        return redirect(url_for('user.manage_profiles'))

    user = UserProfile.query.get_or_404(id)
    is_teacher = user.user_type and user.user_type.TypeName == 'Teacher'

    if is_teacher:
        form = TeacherProfileForm()
        populate_teacher_form_choices(form)
        teacher_type = UserType.query.filter_by(TypeName='Teacher').first()
        if teacher_type:
            form.TypeID.data = teacher_type.TypeID
    else:
        form = StudentProfileForm()
        populate_student_form_choices(form)
        student_type = UserType.query.filter_by(TypeName='Student').first()
        if student_type:
            form.TypeID.data = student_type.TypeID

    if form.validate_on_submit():
        user.Name = form.Name.data
        user.Gender = form.Gender.data
        user.DOB = form.DOB.data
        user.TypeID = form.TypeID.data
        user.AddressID = form.AddressID.data
        user.ContactNoID = form.ContactNoID.data

        if is_teacher:
            user.SubjectID = form.SubjectID.data
            user.GroupID = None
            user.ClassID = None
        else:
            user.GroupID = form.GroupID.data
            user.ClassID = form.ClassID.data
            user.SubjectID = None

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

    flash(f'Failed to update profile: {form.errors}', 'danger')
    return redirect(url_for('user.manage_profiles'))


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

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

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

    pagination = UserType.query.paginate(page=page, per_page=per_page, error_out=False)
    usertypes = pagination.items

    prev_url = url_for('user.manage_usertypes', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('user.manage_usertypes', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('users/usertypes.html', form=form, usertypes=usertypes, per_page=per_page, prev_url=prev_url,
                           next_url=next_url)


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

    flash('Failed to update user type. Please check your inputs.', 'danger')
    return redirect(url_for('user.manage_usertypes'))


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

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

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

    pagination = ContactNo.query.paginate(page=page, per_page=per_page, error_out=False)
    contacts = pagination.items

    prev_url = url_for('user.manage_contacts', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('user.manage_contacts', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('users/contacts.html', form=form, contacts=contacts, per_page=per_page, prev_url=prev_url,
                           next_url=next_url)


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

    flash('Failed to update contact. Please check your inputs.', 'danger')
    return redirect(url_for('user.manage_contacts'))


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

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

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

    pagination = Address.query.paginate(page=page, per_page=per_page, error_out=False)
    addresses = pagination.items

    prev_url = url_for('user.manage_addresses', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('user.manage_addresses', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('users/addresses.html', form=form, addresses=addresses, per_page=per_page, prev_url=prev_url,
                           next_url=next_url)


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

    flash('Failed to update address. Please check your inputs.', 'danger')
    return redirect(url_for('user.manage_addresses'))


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