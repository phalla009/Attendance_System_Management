from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.academic_form import ClassForm
from models.academic import Class, Session

from . import academic_bp


@academic_bp.route('/classes', methods=['GET', 'POST'])
@login_required
def manage_classes():
    form = ClassForm()
    form.SessionID.choices = [(s.SessionID, s.Session_name) for s in Session.query.all()]

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', '', type=str)
    session_filter = request.args.get('session_id', '', type=int)

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
    elif request.method == 'POST':
        flash('Please correct the errors in the form.', 'danger')

    query = (
        db.session.query(Class, Session.Session_name.label('SessionName'))
        .join(Session, Class.SessionID == Session.SessionID)
    )

    if search_query:
        query = query.filter(
            (Class.Code.ilike(f'%{search_query}%')) |
            (Class.Name.ilike(f'%{search_query}%'))
        )

    if session_filter:
        query = query.filter(Class.SessionID == session_filter)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    classes = pagination.items

    prev_url = url_for('academic.manage_classes', page=pagination.prev_num, per_page=per_page, q=search_query,
                       session_id=session_filter) if pagination.has_prev else None
    next_url = url_for('academic.manage_classes', page=pagination.next_num, per_page=per_page, q=search_query,
                       session_id=session_filter) if pagination.has_next else None

    sessions = Session.query.all()

    return render_template('academic/classes.html', form=form, classes=classes, sessions=sessions,
                           per_page=per_page, prev_url=prev_url, next_url=next_url,
                           search_query=search_query, session_filter=session_filter)


@academic_bp.route('/classes/edit/<int:id>', methods=['POST'])
@login_required
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

    return render_template('academic/classes.html', form=form, classes=classes, per_page=per_page,
                           edit_error_id=id)


@academic_bp.route('/classes/delete/<int:id>', methods=['POST'])
@login_required
def delete_class(id):
    class_obj = Class.query.get_or_404(id)
    try:
        db.session.delete(class_obj)
        db.session.commit()
        flash('Class deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this class because it is related to other data.', 'danger')
    return redirect(url_for('academic.manage_classes'))