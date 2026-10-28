from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.location_form import ProvinceForm
from models.location import Province
from . import location_bp


@location_bp.route('/provinces', methods=['GET', 'POST'])
@login_required
def manage_provinces():
    form = ProvinceForm()
    if form.validate_on_submit():
        province = Province(Code=form.Code.data, Name=form.Name.data)
        db.session.add(province)
        db.session.commit()
        flash('Province added successfully!', 'success')
        return redirect(url_for('location.manage_provinces'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Province.query.paginate(page=page, per_page=per_page, error_out=False)
    provinces = pagination.items

    prev_url = url_for('location.manage_provinces', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None
    next_url = url_for('location.manage_provinces', page=pagination.next_num, per_page=per_page) if pagination.has_next else None

    return render_template(
        'locations/provinces.html',
        form=form,
        provinces=provinces,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url
    )


@location_bp.route('/provinces/edit/<int:id>', methods=['POST'])
@login_required
def edit_province(id):
    province = Province.query.get_or_404(id)
    form = ProvinceForm()

    if form.validate_on_submit():
        province.Name = form.Name.data
        db.session.commit()
        flash('Province updated successfully!', 'success')
        return redirect(url_for('location.manage_provinces'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Province.query.paginate(page=page, per_page=per_page, error_out=False)
    provinces = pagination.items

    flash('Failed to update province. Please check your input.', 'danger')
    return render_template(
        'locations/provinces.html',
        form=form,
        provinces=provinces,
        per_page=per_page,
        prev_url=url_for('location.manage_provinces', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None,
        next_url=url_for('location.manage_provinces', page=pagination.next_num, per_page=per_page) if pagination.has_next else None,
        edit_error_id=id
    )


@location_bp.route('/provinces/delete/<int:id>', methods=['POST'])
@login_required
def delete_province(id):
    province = Province.query.get_or_404(id)
    try:
        db.session.delete(province)
        db.session.commit()
        flash('Province deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this province because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_provinces'))