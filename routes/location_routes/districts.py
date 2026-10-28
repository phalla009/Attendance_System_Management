from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.location_form import DistrictForm
from models.location import District, Province
from . import location_bp


@location_bp.route('/districts', methods=['GET', 'POST'])
@login_required
def manage_districts():
    form = DistrictForm()
    form.ProvinceID.choices = [(p.ProvinceID, p.Name) for p in Province.query.all()]
    if form.validate_on_submit():
        district = District(
            Code=form.Code.data,
            Name=form.Name.data,
            ProvinceID=form.ProvinceID.data,
        )
        db.session.add(district)
        db.session.commit()
        flash('District added successfully!', 'success')
        return redirect(url_for('location.manage_districts'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = District.query.paginate(page=page, per_page=per_page, error_out=False)
    districts = pagination.items

    prev_url = url_for('location.manage_districts', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None
    next_url = url_for('location.manage_districts', page=pagination.next_num, per_page=per_page) if pagination.has_next else None

    return render_template(
        'locations/districts.html',
        form=form,
        districts=districts,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url
    )


@location_bp.route('/districts/edit/<int:id>', methods=['POST'])
@login_required
def edit_district(id):
    district = District.query.get_or_404(id)
    form = DistrictForm()
    form.ProvinceID.choices = [(p.ProvinceID, p.Name) for p in Province.query.all()]

    if form.validate_on_submit():
        district.Name = form.Name.data
        district.ProvinceID = form.ProvinceID.data
        db.session.commit()
        flash('District updated successfully!', 'success')
        return redirect(url_for('location.manage_districts'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = District.query.paginate(page=page, per_page=per_page, error_out=False)
    districts = pagination.items

    flash('Failed to update district. Please check your input.', 'danger')
    return render_template(
        'locations/districts.html',
        form=form,
        districts=districts,
        per_page=per_page,
        prev_url=url_for('location.manage_districts', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None,
        next_url=url_for('location.manage_districts', page=pagination.next_num, per_page=per_page) if pagination.has_next else None,
        edit_error_id=id
    )


@location_bp.route('/districts/delete/<int:id>', methods=['POST'])
@login_required
def delete_district(id):
    district = District.query.get_or_404(id)
    try:
        db.session.delete(district)
        db.session.commit()
        flash('District deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this district because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_districts'))