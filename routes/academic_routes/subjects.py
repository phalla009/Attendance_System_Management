from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.academic_form import SubjectForm
from models.academic import Subject

from . import academic_bp


@academic_bp.route('/subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    form = SubjectForm()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', '', type=str)

    if form.validate_on_submit():
        subject = Subject(Code=form.Code.data, Name=form.Name.data)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('academic.manage_subjects'))
    elif request.method == 'POST':
        flash('Please correct the errors in the form.', 'danger')

    query = Subject.query

    if search_query:
        query = query.filter(
            (Subject.Code.ilike(f'%{search_query}%')) |
            (Subject.Name.ilike(f'%{search_query}%'))
        )

    pagination = query.order_by(Subject.SubjectID).paginate(page=page, per_page=per_page, error_out=False)
    subjects = pagination.items

    prev_url = url_for('academic.manage_subjects', page=pagination.prev_num, per_page=per_page,
                       q=search_query) if pagination.has_prev else None
    next_url = url_for('academic.manage_subjects', page=pagination.next_num, per_page=per_page,
                       q=search_query) if pagination.has_next else None

    return render_template('academic/subjects.html', form=form, subjects=subjects, per_page=per_page,
                           prev_url=prev_url, next_url=next_url, search_query=search_query)


@academic_bp.route('/subjects/edit/<int:id>', methods=['POST'])
@login_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    form = SubjectForm()
    form._subject_id = id

    if form.validate_on_submit():
        subject.Code = form.Code.data
        subject.Name = form.Name.data
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('academic.manage_subjects'))

    flash('Please correct the errors in the form.', 'danger')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Subject.query.order_by(Subject.SubjectID).paginate(page=page, per_page=per_page,
                                                                    error_out=False)
    subjects = pagination.items

    return render_template('academic/subjects.html', form=form, subjects=subjects, per_page=per_page,
                           edit_error_id=id)


@academic_bp.route('/subjects/delete/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this subject because it is related to other data.', 'danger')
    return redirect(url_for('academic.manage_subjects'))