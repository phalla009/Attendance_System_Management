import io
import os
import uuid
from flask import (
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_login import login_required
import pandas as pd
from werkzeug.utils import secure_filename
from extensions import db
from forms.user_form import StudentProfileForm, TeacherProfileForm
from models.academic import Group
from models.location import Address, Commune, District, Province, Village
from models.user import UserProfile, UserType
from . import (
    populate_student_form_choices,
    populate_teacher_form_choices,
    user_bp,
)


# ======================= HELPERS =======================

def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def save_photo(photo_file):
    """Save uploaded photo and return the new filename (or None)."""
    if not photo_file:
        return None
    filename = secure_filename(photo_file.filename or '')
    if not filename:
        return None
    upload_folder = os.path.join(
        current_app.root_path, 'static', 'uploads', 'profiles'
    )
    os.makedirs(upload_folder, exist_ok=True)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    photo_filename = f'{uuid.uuid4().hex}.{ext}'
    photo_file.save(os.path.join(upload_folder, photo_filename))
    return photo_filename


def get_or_create_address(form):
    """Read home/street/province/district/commune/village from the form,
    find a matching Address (or create one) and return its AddressID."""
    home = (form.get('home') or '').strip() or None
    street = (form.get('street') or '').strip() or None
    province_id = _to_int(form.get('province_id'))
    district_id = _to_int(form.get('district_id'))
    commune_id = _to_int(form.get('commune_id'))
    village_id = _to_int(form.get('village_id'))

    if not any([home, street, province_id, district_id, commune_id, village_id]):
        return None

    addr = Address.query.filter_by(
        Home=home,
        Street=street,
        ProvinceID=province_id,
        DistrictID=district_id,
        CommuneID=commune_id,
        VillageID=village_id,
    ).first()

    if not addr:
        addr = Address(
            Home=home,
            Street=street,
            ProvinceID=province_id,
            DistrictID=district_id,
            CommuneID=commune_id,
            VillageID=village_id,
        )
        db.session.add(addr)
        db.session.flush()

    return addr.AddressID


def build_address(addr):
    """Full address as one line (used in Excel export)."""
    if not addr:
        return '-'
    parts = [
        f'ផ្ទះលេខ {addr.Home}' if addr.Home else None,
        f'ផ្លូវ {addr.Street}' if addr.Street else None,
        f'ភូមិ {addr.village.Name}' if addr.village else None,
        f'ឃុំ/សង្កាត់ {addr.commune.Name}' if addr.commune else None,
        f'ស្រុក/ខណ្ឌ {addr.district.Name}' if addr.district else None,
        f'{addr.province.Name}' if addr.province else None,
    ]
    return ', '.join(p for p in parts if p) or '-'


# ======================= CASCADE API =======================

@user_bp.route('/api/districts/<int:province_id>', methods=['GET'])
@login_required
def api_districts(province_id):
    rows = (
        District.query.filter_by(ProvinceID=province_id)
        .order_by(District.Name)
        .all()
    )
    return jsonify([{'id': r.DistrictID, 'name': r.Name} for r in rows])


@user_bp.route('/api/communes/<int:district_id>', methods=['GET'])
@login_required
def api_communes(district_id):
    rows = (
        Commune.query.filter_by(DistrictID=district_id)
        .order_by(Commune.Name)
        .all()
    )
    return jsonify([{'id': r.CommuneID, 'name': r.Name} for r in rows])


@user_bp.route('/api/villages/<int:commune_id>', methods=['GET'])
@login_required
def api_villages(commune_id):
    rows = (
        Village.query.filter_by(CommuneID=commune_id)
        .order_by(Village.Name)
        .all()
    )
    return jsonify([{'id': r.VillageID, 'name': r.Name} for r in rows])


# ======================= LIST =======================

@user_bp.route('/profiles', methods=['GET'])
@login_required
def manage_profiles():
    student_form = StudentProfileForm()
    teacher_form = TeacherProfileForm()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', '', type=str)
    type_filter = request.args.get('type_id', '', type=int)
    group_filter = request.args.get('group_id', '', type=int)

    populate_student_form_choices(student_form)
    populate_teacher_form_choices(teacher_form)

    query = UserProfile.query

    if search_query:
        query = query.filter(
            (UserProfile.Code.ilike(f'%{search_query}%'))
            | (UserProfile.Name.ilike(f'%{search_query}%'))
        )

    if type_filter:
        query = query.filter(UserProfile.TypeID == type_filter)

    if group_filter:
        query = query.filter(UserProfile.GroupID == group_filter)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    profiles = pagination.items

    prev_url = (
        url_for(
            'user.manage_profiles',
            page=pagination.prev_num,
            per_page=per_page,
            q=search_query,
            type_id=type_filter,
            group_id=group_filter,
        )
        if pagination.has_prev
        else None
    )
    next_url = (
        url_for(
            'user.manage_profiles',
            page=pagination.next_num,
            per_page=per_page,
            q=search_query,
            type_id=type_filter,
            group_id=group_filter,
        )
        if pagination.has_next
        else None
    )

    user_types = UserType.query.all()
    groups = Group.query.all()
    provinces = Province.query.order_by(Province.Name).all()

    return render_template(
        'users/profiles.html',
        student_form=student_form,
        teacher_form=teacher_form,
        profiles=profiles,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url,
        search_query=search_query,
        type_filter=type_filter,
        group_filter=group_filter,
        user_types=user_types,
        groups=groups,
        provinces=provinces,
    )


# ======================= ADD =======================

@user_bp.route('/profiles/add-student', methods=['POST'])
@login_required
def manage_students():
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can add student profiles.', 'danger')
        return redirect(url_for('user.manage_profiles'))

    student_form = StudentProfileForm()
    populate_student_form_choices(student_form)
    del student_form.AddressID  # address is handled by get_or_create_address

    student_type = UserType.query.filter_by(TypeName='Student').first()
    if student_type:
        student_form.TypeID.data = student_type.TypeID

    if student_form.validate_on_submit():
        photo_filename = save_photo(student_form.Photo.data)

        user = UserProfile(
            Code=student_form.Code.data,
            Name=student_form.Name.data,
            Gender=student_form.Gender.data,
            DOB=student_form.DOB.data,
            Photo=photo_filename,
            TypeID=student_form.TypeID.data,
            GroupID=student_form.GroupID.data,
            AddressID=get_or_create_address(request.form),
            ContactNoID=student_form.ContactNoID.data,
        )
        db.session.add(user)
        db.session.commit()
        flash('Student Profile added successfully!', 'success')
        return redirect(url_for('user.manage_profiles'))

    flash(f'Failed to add student profile: {student_form.errors}', 'danger')
    return redirect(url_for('user.manage_profiles'))


@user_bp.route('/profiles/add-teacher', methods=['POST'])
@login_required
def manage_teachers():
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can add teacher profiles.', 'danger')
        return redirect(url_for('user.manage_profiles'))

    teacher_form = TeacherProfileForm()
    populate_teacher_form_choices(teacher_form)
    del teacher_form.AddressID  # address is handled by get_or_create_address

    teacher_type = UserType.query.filter_by(TypeName='Teacher').first()
    if teacher_type:
        teacher_form.TypeID.data = teacher_type.TypeID

    if teacher_form.validate_on_submit():
        photo_filename = save_photo(teacher_form.Photo.data)

        user = UserProfile(
            Code=teacher_form.Code.data,
            Name=teacher_form.Name.data,
            Gender=teacher_form.Gender.data,
            DOB=teacher_form.DOB.data,
            Photo=photo_filename,
            TypeID=teacher_form.TypeID.data,
            SubjectID=teacher_form.SubjectID.data,
            AddressID=get_or_create_address(request.form),
            ContactNoID=teacher_form.ContactNoID.data,
        )
        db.session.add(user)
        db.session.commit()
        flash('Teacher Profile added successfully!', 'success')
        return redirect(url_for('user.manage_profiles'))

    flash(f'Failed to add teacher profile: {teacher_form.errors}', 'danger')
    return redirect(url_for('user.manage_profiles'))


# ======================= EDIT =======================

@user_bp.route('/profiles/edit/<int:id>', methods=['POST'])
@login_required
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

    del form.AddressID  # address is handled by get_or_create_address

    if form.validate_on_submit():
        user.Name = form.Name.data
        user.Gender = form.Gender.data
        user.DOB = form.DOB.data
        user.TypeID = form.TypeID.data
        user.AddressID = get_or_create_address(request.form)
        user.ContactNoID = form.ContactNoID.data

        if is_teacher:
            user.SubjectID = form.SubjectID.data
            user.GroupID = None
        else:
            user.GroupID = form.GroupID.data
            user.SubjectID = None

        new_photo = save_photo(form.Photo.data)
        if new_photo:
            user.Photo = new_photo

        db.session.commit()
        flash('User Profile updated successfully!', 'success')
        return redirect(url_for('user.manage_profiles'))

    flash(f'Failed to update profile: {form.errors}', 'danger')
    return redirect(url_for('user.manage_profiles'))


# ======================= DELETE =======================

@user_bp.route('/profiles/delete/<int:id>', methods=['POST'])
@login_required
def delete_profile(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can delete user profiles.', 'danger')
        return redirect(url_for('user.manage_profiles'))

    user = UserProfile.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User Profile deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash(
            'Cannot delete this profile because it is linked to other'
            ' records!',
            'danger',
        )

    return redirect(url_for('user.manage_profiles'))


# ======================= EXPORT EXCEL =======================

@user_bp.route('/profiles/export-excel', methods=['GET'])
@login_required
def export_students_excel():
    student_type = UserType.query.filter_by(TypeName='Student').first()
    type_id = student_type.TypeID if student_type else None

    if type_id:
        students = UserProfile.query.filter_by(TypeID=type_id).all()
    else:
        students = UserProfile.query.all()

    data = []
    for index, u in enumerate(students, start=1):
        gender_str = (
            'Male' if u.Gender == 'M' else ('Female' if u.Gender == 'F' else '-')
        )
        dob_str = u.DOB.strftime('%Y-%m-%d') if u.DOB else '-'
        user_type_name = u.user_type.TypeName if u.user_type else '-'
        group_name = u.group_rel.Name if u.group_rel else '-'
        contact_str = u.contact_rel.ContactNumber if u.contact_rel else '-'
        addr = u.address_rel

        data.append({
            'No.': index,
            'Code': u.Code,
            'Full Name': u.Name,
            'Gender': gender_str,
            'Date of Birth': dob_str,
            'User Type': user_type_name,
            'Group': group_name,
            'Contact Number': contact_str,
            'Home': (addr.Home or '-') if addr else '-',
            'Street': (addr.Street or '-') if addr else '-',
            'Village': addr.village.Name if addr and addr.village else '-',
            'Commune': addr.commune.Name if addr and addr.commune else '-',
            'District': addr.district.Name if addr and addr.district else '-',
            'Province': addr.province.Name if addr and addr.province else '-',
            'Full Address': build_address(addr),
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students List')

        ws = writer.sheets['Students List']
        for col in ws.columns:
            max_len = max(len(str(c.value)) if c.value else 0 for c in col)
            ws.column_dimensions[col[0].column_letter].width = min(
                max_len + 4, 60
            )

    output.seek(0)

    return send_file(
        output,
        mimetype=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ),
        as_attachment=True,
        download_name='Students_List.xlsx',
    )


# ======================= IMPORT EXCEL =======================

@user_bp.route('/profiles/import-excel', methods=['POST'])
@login_required
def import_students_excel():
    if session.get('user_type') != 'Teacher':
        flash(
            'Access Denied! Only Teachers can import student profiles.',
            'danger',
        )
        return redirect(url_for('user.manage_profiles'))

    # Template uses name="file"; also accept "excel_file" for safety.
    file = request.files.get('file') or request.files.get('excel_file')
    if file is None:
        flash('No file part uploaded!', 'danger')
        return redirect(url_for('user.manage_profiles'))

    if file.filename == '':
        flash('No selected file!', 'danger')
        return redirect(url_for('user.manage_profiles'))

    if file.filename.lower().endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(file)

            student_type = UserType.query.filter_by(TypeName='Student').first()
            student_type_id = student_type.TypeID if student_type else 2

            imported_count = 0
            updated_count = 0

            with db.session.no_autoflush:
                for _, row in df.iterrows():
                    code = str(row.get('Code', '')).strip()
                    name = str(row.get('Full Name', '')).strip()

                    if (
                        not code
                        or not name
                        or code.lower() == 'nan'
                        or name.lower() == 'nan'
                    ):
                        continue

                    raw_gender = str(row.get('Gender', 'M')).strip().upper()
                    gender = 'M' if raw_gender in ['M', 'MALE'] else 'F'

                    raw_dob = row.get('Date of Birth')
                    dob = None
                    if (
                        pd.notna(raw_dob)
                        and str(raw_dob).strip() not in ['', '-', 'nan', 'NaT']
                    ):
                        try:
                            dob = pd.to_datetime(raw_dob).date()
                        except Exception:
                            dob = None

                    group_id = None
                    group_name = str(row.get('Group', '')).strip()
                    if group_name and group_name.lower() not in ['nan', '-']:
                        group_obj = Group.query.filter_by(
                            Name=group_name
                        ).first()
                        if group_obj:
                            group_id = group_obj.GroupID

                    existing_user = UserProfile.query.filter_by(
                        Code=code
                    ).first()

                    if existing_user:
                        existing_user.Name = name
                        existing_user.Gender = gender
                        existing_user.DOB = dob
                        existing_user.TypeID = student_type_id
                        existing_user.GroupID = group_id
                        updated_count += 1
                    else:
                        user = UserProfile(
                            Code=code,
                            Name=name,
                            Gender=gender,
                            DOB=dob,
                            TypeID=student_type_id,
                            GroupID=group_id,
                        )
                        db.session.add(user)
                        imported_count += 1

            db.session.commit()
            flash(
                f'Successfully imported {imported_count} new and updated'
                f' {updated_count} student profiles!',
                'success',
            )
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing Excel file: {str(e)}', 'danger')
    else:
        flash(
            'Invalid file format! Please upload a valid .xlsx or .xls file.',
            'danger',
        )

    return redirect(url_for('user.manage_profiles'))


# ======================= VIEW =======================

@user_bp.route('/profiles/view/<int:id>', methods=['GET'])
@login_required
def view_profile(id):
    profile = UserProfile.query.get_or_404(id)
    return render_template('users/view_profile.html', profile=profile)