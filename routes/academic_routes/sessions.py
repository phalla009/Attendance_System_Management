from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.academic_form import SessionForm
from models.academic import Session

from . import academic_bp


@academic_bp.route('/sessions', methods=['GET', 'POST'])
@login_required
def manage_sessions():
    form = SessionForm()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', '', type=str)

    if form.validate_on_submit():
        session = Session(Code=form.Code.data, Session_name=form.Session_name.data)
        db.session.add(session)
        db.session.commit()
        flash('Session added successfully!', 'success')
        return redirect(url_for('academic.manage_sessions'))
    elif request.method == 'POST':
        flash('Please correct the errors in the form.', 'danger')

    query = Session.query
    if search_query:
        query = query.filter(
            (Session.Code.ilike(f'%{search_query}%')) |
            (Session.Session_name.ilike(f'%{search_query}%'))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    sessions = pagination.items

    prev_url = url_for('academic.manage_sessions', page=pagination.prev_num, per_page=per_page,
                       q=search_query) if pagination.has_prev else None
    next_url = url_for('academic.manage_sessions', page=pagination.next_num, per_page=per_page,
                       q=search_query) if pagination.has_next else None

    return render_template('academic/sessions.html', form=form, sessions=sessions, per_page=per_page,
                           prev_url=prev_url, next_url=next_url, search_query=search_query)


@academic_bp.route('/sessions/edit/<int:id>', methods=['POST'])
@login_required
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

    return render_template('academic/sessions.html', form=form, sessions=sessions, per_page=per_page,
                           edit_error_id=id)


@academic_bp.route('/sessions/delete/<int:id>', methods=['POST'])
@login_required
def delete_session(id):
    session = Session.query.get_or_404(id)
    try:
        db.session.delete(session)
        db.session.commit()
        flash('Session deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this session because it is related to other data.', 'danger')
    return redirect(url_for('academic.manage_sessions'))