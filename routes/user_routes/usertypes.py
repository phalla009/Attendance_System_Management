from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required
from extensions import db
from forms.user_form import UserTypeForm
from models.user import UserType
from . import user_bp


@user_bp.route('/usertypes', methods=['GET', 'POST'])
@login_required
def manage_usertypes():
    form = UserTypeForm()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if request.method == 'POST':
        if session.get('user_type') != 'Admin':
            flash('Access Denied! Only Admin can add user types.', 'danger')
            return redirect(url_for('user.manage_usertypes'))

        if form.validate_on_submit():
            usertype = UserType(
                Code=form.Code.data, TypeName=form.TypeName.data
            )
            db.session.add(usertype)
            db.session.commit()
            flash('User Type added successfully!', 'success')
            return redirect(url_for('user.manage_usertypes'))

    pagination = UserType.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    usertypes = pagination.items

    prev_url = (
        url_for('user.manage_usertypes', page=pagination.prev_num, per_page=per_page)
        if pagination.has_prev
        else None
    )
    next_url = (
        url_for('user.manage_usertypes', page=pagination.next_num, per_page=per_page)
        if pagination.has_next
        else None
    )

    return render_template(
        'users/usertypes.html',
        form=form,
        usertypes=usertypes,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url,
    )


@user_bp.route('/usertypes/edit/<int:id>', methods=['POST'])
@login_required
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
@login_required
def delete_usertype(id):
    if session.get('user_type') != 'Admin':
        flash('Access Denied! Only Admin can delete user types.', 'danger')
        return redirect(url_for('user.manage_usertypes'))

    usertype = UserType.query.get_or_404(id)
    try:
        db.session.delete(usertype)
        db.session.commit()
        flash('User Type deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash(
            'Cannot delete this user type because it is linked to other'
            ' records!',
            'danger',
        )

    return redirect(url_for('user.manage_usertypes'))