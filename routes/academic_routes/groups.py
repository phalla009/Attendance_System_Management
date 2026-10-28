from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.academic_form import GroupForm
from models.academic import Group, Session
from models.user import UserProfile
from sqlalchemy import func

from . import academic_bp


@academic_bp.route('/groups', methods=['GET', 'POST'])
@login_required
def manage_groups():
    form = GroupForm()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', '', type=str)

    if form.validate_on_submit():
        group = Group(
            Code=form.Code.data,
            Name=form.Name.data,
            ScheduleID=form.ScheduleID.data,
        )
        db.session.add(group)
        db.session.commit()
        flash('Group added successfully!', 'success')
        return redirect(url_for('academic.manage_groups'))
    elif request.method == 'POST':
        flash('Please correct the errors in the form.', 'danger')

    query = Group.query

    if search_query:
        query = query.filter(
            (Group.Code.ilike(f'%{search_query}%')) |
            (Group.Name.ilike(f'%{search_query}%'))
        )

    pagination = query.order_by(Group.GroupID).paginate(page=page, per_page=per_page, error_out=False)
    groups = pagination.items

    prev_url = url_for('academic.manage_groups', page=pagination.prev_num, per_page=per_page,
                       q=search_query) if pagination.has_prev else None
    next_url = url_for('academic.manage_groups', page=pagination.next_num, per_page=per_page,
                       q=search_query) if pagination.has_next else None

    total_groups = Group.query.count()

    return render_template('academic/groups.html', form=form, groups=groups, per_page=per_page,
                           prev_url=prev_url, next_url=next_url, search_query=search_query,
                           total_groups=total_groups)


@academic_bp.route('/groups/edit/<int:id>', methods=['POST'])
@login_required
def edit_group(id):
    group = Group.query.get_or_404(id)
    form = GroupForm()
    form._group_id = id

    if form.validate_on_submit():
        group.Code = form.Code.data
        group.Name = form.Name.data
        group.ScheduleID = form.ScheduleID.data
        db.session.commit()
        flash('Group updated successfully!', 'success')
        return redirect(url_for('academic.manage_groups'))

    flash('Please correct the errors in the form.', 'danger')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Group.query.order_by(Group.GroupID).paginate(page=page, per_page=per_page, error_out=False)
    groups = pagination.items

    return render_template('academic/groups.html', form=form, groups=groups, per_page=per_page,
                           total_groups=Group.query.count(), edit_error_id=id)


@academic_bp.route('/groups/delete/<int:id>', methods=['POST'])
@login_required
def delete_group(id):
    group = Group.query.get_or_404(id)
    try:
        db.session.delete(group)
        db.session.commit()
        flash('Group deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this group because it is related to other data.', 'danger')
    return redirect(url_for('academic.manage_groups'))


@academic_bp.route('/groups/cards', methods=['GET'])
@login_required
def groups_cards():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)
    search_query = request.args.get('q', '', type=str)

    # Query groups along with session name and student count
    query = db.session.query(
        Group,
        Session.Session_name,
        db.func.count(UserProfile.ProfileID).label('total_students')
    ).outerjoin(Session, Group.ScheduleID == Session.SessionID)\
     .outerjoin(UserProfile, Group.GroupID == UserProfile.GroupID)

    if search_query:
        query = query.filter(
            (Group.Code.ilike(f'%{search_query}%')) |
            (Group.Name.ilike(f'%{search_query}%'))
        )

    query = query.group_by(Group.GroupID, Session.Session_name)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    groups = pagination.items  # This will now contain tuples of (Group, session_name, total_students)

    return render_template(
        'academic/groups_cards.html',
        groups=groups,
        pagination=pagination,
        per_page=per_page,
        search_query=search_query
    )


@academic_bp.route('/groups/<int:group_id>/students', methods=['GET'])
@login_required
def group_students(group_id):
    group = Group.query.get_or_404(group_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '', type=str)

    query = UserProfile.query.filter_by(GroupID=group_id)
    total_students = query.count()
    male_count = query.filter(UserProfile.Gender == 'M').count()
    female_count = query.filter(UserProfile.Gender == 'F').count()

    if search_query:
        query = query.filter(
            (UserProfile.Name.ilike(f'%{search_query}%')) |
            (UserProfile.Code.ilike(f'%{search_query}%'))
        )

    filtered_count = query.count()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items

    prev_url = url_for('academic.group_students', group_id=group_id, page=pagination.prev_num,
                       per_page=per_page, search=search_query) if pagination.has_prev else None
    next_url = url_for('academic.group_students', group_id=group_id, page=pagination.next_num,
                       per_page=per_page, search=search_query) if pagination.has_next else None

    return render_template('academic/group_students.html',
                           group=group,
                           students=students,
                           total_students=total_students,
                           male_count=male_count,
                           female_count=female_count,
                           filtered_count=filtered_count,
                           pagination=pagination,
                           per_page=per_page,
                           prev_url=prev_url,
                           next_url=next_url,
                           search_query=search_query)