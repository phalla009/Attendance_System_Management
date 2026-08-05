from extensions import db
from flask import Blueprint, flash, redirect, render_template, request, url_for
from forms.academic_form import ClassForm, GroupForm, SessionForm, SubjectForm
from models.academic import Class, Group, Session, Subject

academic_bp = Blueprint('academic', __name__, url_prefix='/academic')


# ==================== HOME / INDEX ROUTE ====================
@academic_bp.route('/index')
def index():
    total_sessions = Session.query.count()
    total_classes = Class.query.count()
    total_groups = Group.query.count()
    total_subjects = Subject.query.count()

    return render_template(
        'academic/index.html',
        active_page='index',
        total_sessions=total_sessions,
        total_classes=total_classes,
        total_groups=total_groups,
        total_subjects=total_subjects
    )


# ==================== SESSIONS ROUTES ====================
@academic_bp.route('/sessions', methods=['GET', 'POST'])
def manage_sessions():
    form = SessionForm()

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if form.validate_on_submit():
        session = Session(Code=form.Code.data, Session_name=form.Session_name.data)
        db.session.add(session)
        db.session.commit()
        flash('Session added successfully!', 'success')
        return redirect(url_for('academic.manage_sessions'))

    pagination = Session.query.paginate(page=page, per_page=per_page, error_out=False)
    sessions = pagination.items

    prev_url = url_for('academic.manage_sessions', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('academic.manage_sessions', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('academic/sessions.html', form=form, sessions=sessions, per_page=per_page, prev_url=prev_url,
                           next_url=next_url)


@academic_bp.route('/sessions/edit/<int:id>', methods=['POST'])
def edit_session(id):
    session = Session.query.get_or_404(id)
    form = SessionForm()
    form._session_id = id

    if form.validate_on_submit():
        session.Code = form.Code.data
        session.Session_name = form.Session_name.data
        db.session.commit()
        flash('Session updated successfully!', 'success')
        return redirect(url_for('academic.manage_sessions'))

    flash('Please correct the errors in the form.', 'danger')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Session.query.paginate(page=page, per_page=per_page, error_out=False)
    sessions = pagination.items

    return render_template('academic/sessions.html', form=form, sessions=sessions, per_page=per_page, edit_error_id=id)


@academic_bp.route('/sessions/delete/<int:id>', methods=['POST'])
def delete_session(id):
    session = Session.query.get_or_404(id)
    try:
        db.session.delete(session)
        db.session.commit()
        flash('Session deleted successfully!', 'danger')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this session because it is related to other data.', 'danger')
    return redirect(url_for('academic.manage_sessions'))


# ==================== CLASSES ROUTES ====================
@academic_bp.route('/classes', methods=['GET', 'POST'])
def manage_classes():
    form = ClassForm()
    form.SessionID.choices = [(s.SessionID, s.Session_name) for s in Session.query.all()]

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if form.validate_on_submit():
        new_class = Class(
            Code=form.Code.data,
            Name=form.Name.data,
            SessionID=form.SessionID.data,
        )
        db.session.add(new_class)
        db.session.commit()
        flash('Class added successfully!', 'success')
        return redirect(url_for('academic.manage_classes'))

    query = (
        db.session.query(Class, Session.Session_name.label('SessionName'))
        .join(Session, Class.SessionID == Session.SessionID)
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    classes = pagination.items

    prev_url = url_for('academic.manage_classes', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('academic.manage_classes', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('academic/classes.html', form=form, classes=classes, per_page=per_page, prev_url=prev_url,
                           next_url=next_url)


@academic_bp.route('/classes/edit/<int:id>', methods=['POST'])
def edit_class(id):
    class_obj = Class.query.get_or_404(id)
    form = ClassForm()
    form._class_id = id
    form.SessionID.choices = [(s.SessionID, s.Session_name) for s in Session.query.all()]

    if form.validate_on_submit():
        class_obj.Code = form.Code.data
        class_obj.Name = form.Name.data
        class_obj.SessionID = form.SessionID.data
        db.session.commit()
        flash('Class updated successfully!', 'success')
        return redirect(url_for('academic.manage_classes'))

    flash('Please correct the errors in the form.', 'danger')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = (
        db.session.query(Class, Session.Session_name.label('SessionName'))
        .join(Session, Class.SessionID == Session.SessionID)
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    classes = pagination.items

    return render_template('academic/classes.html', form=form, classes=classes, per_page=per_page, edit_error_id=id)


@academic_bp.route('/classes/delete/<int:id>', methods=['POST'])
def delete_class(id):
    class_obj = Class.query.get_or_404(id)
    try:
        db.session.delete(class_obj)
        db.session.commit()
        flash('Class deleted successfully!', 'danger')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this class because it is related to other data.', 'danger')
    return redirect(url_for('academic.manage_classes'))


# ==================== GROUPS ROUTES ====================
@academic_bp.route('/groups', methods=['GET', 'POST'])
def manage_groups():
    form = GroupForm()
    form.SessionID.choices = [(s.SessionID, s.Session_name) for s in Session.query.all()]

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if form.validate_on_submit():
        group = Group(
            Code=form.Code.data,
            Name=form.Name.data,
            SessionID=form.SessionID.data,
            ScheduleID=form.ScheduleID.data,
        )
        db.session.add(group)
        db.session.commit()
        flash('Group added successfully!', 'success')
        return redirect(url_for('academic.manage_groups'))

    query = (
        db.session.query(Group, Session.Session_name.label('SessionName'))
        .join(Session, Group.SessionID == Session.SessionID)
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    groups = pagination.items

    prev_url = url_for('academic.manage_groups', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('academic.manage_groups', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('academic/groups.html', form=form, groups=groups, per_page=per_page, prev_url=prev_url,
                           next_url=next_url)


@academic_bp.route('/groups/edit/<int:id>', methods=['POST'])
def edit_group(id):
    group = Group.query.get_or_404(id)
    form = GroupForm()
    form._group_id = id
    form.SessionID.choices = [(s.SessionID, s.Session_name) for s in Session.query.all()]

    if form.validate_on_submit():
        group.Code = form.Code.data
        group.Name = form.Name.data
        group.SessionID = form.SessionID.data
        group.ScheduleID = form.ScheduleID.data
        db.session.commit()
        flash('Group updated successfully!', 'success')
        return redirect(url_for('academic.manage_groups'))

    flash('Please correct the errors in the form.', 'danger')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = (
        db.session.query(Group, Session.Session_name.label('SessionName'))
        .join(Session, Group.SessionID == Session.SessionID)
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    groups = pagination.items

    return render_template('academic/groups.html', form=form, groups=groups, per_page=per_page, edit_error_id=id)


@academic_bp.route('/groups/delete/<int:id>', methods=['POST'])
def delete_group(id):
    group = Group.query.get_or_404(id)
    try:
        db.session.delete(group)
        db.session.commit()
        flash('Group deleted successfully!', 'danger')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this group because it is related to other data.', 'danger')
    return redirect(url_for('academic.manage_groups'))


# ==================== SUBJECTS ROUTES ====================
@academic_bp.route('/subjects', methods=['GET', 'POST'])
def manage_subjects():
    form = SubjectForm()
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if form.validate_on_submit():
        subject = Subject(
            Code=form.Code.data,
            Name=form.Name.data,
            GroupID=form.GroupID.data
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('academic.manage_subjects'))

    query = (
        db.session.query(Subject, Group.Name.label('GroupName'))
        .join(Group, Subject.GroupID == Group.GroupID)
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    subjects = pagination.items

    prev_url = url_for('academic.manage_subjects', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('academic.manage_subjects', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('academic/subjects.html', form=form, subjects=subjects, per_page=per_page, prev_url=prev_url,
                           next_url=next_url)


@academic_bp.route('/subjects/edit/<int:id>', methods=['POST'])
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    form = SubjectForm()
    form._subject_id = id
    form.GroupID.choices = [(g.GroupID, g.Name) for g in Group.query.all()]

    if form.validate_on_submit():
        subject.Code = form.Code.data
        subject.Name = form.Name.data
        subject.GroupID = form.GroupID.data
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('academic.manage_subjects'))

    flash('Please correct the errors in the form.', 'danger')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = (
        db.session.query(Subject, Group.Name.label('GroupName'))
        .join(Group, Subject.GroupID == Group.GroupID)
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    subjects = pagination.items

    return render_template('academic/subjects.html', form=form, subjects=subjects, per_page=per_page, edit_error_id=id)


@academic_bp.route('/subjects/delete/<int:id>', methods=['POST'])
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully!', 'danger')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this subject because it is related to other data.', 'danger')
    return redirect(url_for('academic.manage_subjects'))


@academic_bp.route('/groups/cards', methods=['GET'])
def groups_cards():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    from models.user import UserProfile
    from sqlalchemy import func

    # ធ្វើ Subquery រាប់ចំនួនសិស្សតាម GroupID
    subq = db.session.query(
        UserProfile.GroupID,
        func.count(UserProfile.ProfileID).label('total_students')
    ).group_by(UserProfile.GroupID).subquery()

    # Join Group ជាមួយ Session និង Subquery រាប់សិស្ស
    query = db.session.query(
        Group,
        Session.Session_name.label('session_name'),
        func.coalesce(subq.c.total_students, 0).label('total_students')
    ) \
    .outerjoin(Session, Group.SessionID == Session.SessionID) \
    .outerjoin(subq, Group.GroupID == subq.c.GroupID)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    groups = pagination.items

    prev_url = url_for('academic.groups_cards', page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('academic.groups_cards', page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('academic/groups_cards.html',
                           groups=groups,
                           per_page=per_page,
                           prev_url=prev_url,
                           next_url=next_url)


@academic_bp.route('/groups/<int:group_id>/students', methods=['GET'])
def group_students(group_id):
    group = Group.query.get_or_404(group_id)

    from models.user import UserProfile

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # គណនាចំនួនសិស្សសរុបក្នុងក្រុមនេះ
    total_students = UserProfile.query.filter_by(GroupID=group_id).count()

    pagination = UserProfile.query.filter_by(GroupID=group_id).paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items

    prev_url = url_for('academic.group_students', group_id=group_id, page=pagination.prev_num,
                       per_page=per_page) if pagination.has_prev else None
    next_url = url_for('academic.group_students', group_id=group_id, page=pagination.next_num,
                       per_page=per_page) if pagination.has_next else None

    return render_template('academic/group_students.html',
                           group=group,
                           students=students,
                           total_students=total_students,
                           pagination=pagination,
                           per_page=per_page,
                           prev_url=prev_url,
                           next_url=next_url)