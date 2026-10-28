from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required
from extensions import db
from forms.user_form import ContactNoForm
from models.user import ContactNo
from . import user_bp


@user_bp.route('/contacts', methods=['GET', 'POST'])
@login_required
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

    pagination = ContactNo.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    contacts = pagination.items

    prev_url = (
        url_for('user.manage_contacts', page=pagination.prev_num, per_page=per_page)
        if pagination.has_prev
        else None
    )
    next_url = (
        url_for('user.manage_contacts', page=pagination.next_num, per_page=per_page)
        if pagination.has_next
        else None
    )

    return render_template(
        'users/contacts.html',
        form=form,
        contacts=contacts,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url,
    )


@user_bp.route('/contacts/edit/<int:id>', methods=['POST'])
@login_required
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
@login_required
def delete_contact(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can delete contacts.', 'danger')
        return redirect(url_for('user.manage_contacts'))

    contact = ContactNo.query.get_or_404(id)
    try:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact Number deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash(
            'Cannot delete this contact because it is linked to user'
            ' profiles!',
            'danger',
        )

    return redirect(url_for('user.manage_contacts'))