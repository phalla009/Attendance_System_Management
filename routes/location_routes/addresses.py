from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.location_form import AddressForm
from models.location import Address, Commune, District, Province, Village
from . import location_bp


@location_bp.route('/addresses', methods=['GET', 'POST'])
@login_required
def manage_addresses():
    form = AddressForm()
    form.ProvinceID.choices = [(p.ProvinceID, p.Name) for p in Province.query.all()]
    form.DistrictID.choices = [(d.DistrictID, d.Name) for d in District.query.all()]
    form.CommuneID.choices = [(c.CommuneID, c.Name) for c in Commune.query.all()]
    form.VillageID.choices = [(v.VillageID, v.Name) for v in Village.query.all()]

    if form.validate_on_submit():
        address = Address(
            Home=form.Home.data,
            Street=form.Street.data,
            ProvinceID=form.ProvinceID.data,
            DistrictID=form.DistrictID.data,
            CommuneID=form.CommuneID.data,
            VillageID=form.VillageID.data,
        )
        db.session.add(address)
        db.session.commit()
        flash('Address added successfully!', 'success')
        return redirect(url_for('location.manage_addresses'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Address.query.paginate(page=page, per_page=per_page, error_out=False)
    addresses = pagination.items

    prev_url = url_for('location.manage_addresses', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None
    next_url = url_for('location.manage_addresses', page=pagination.next_num, per_page=per_page) if pagination.has_next else None

    return render_template(
        'locations/addresses.html',
        form=form,
        addresses=addresses,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url
    )


@location_bp.route('/addresses/edit/<int:id>', methods=['POST'])
@login_required
def edit_address(id):
    address = Address.query.get_or_404(id)
    form = AddressForm()
    form.ProvinceID.choices = [(p.ProvinceID, p.Name) for p in Province.query.all()]
    form.DistrictID.choices = [(d.DistrictID, d.Name) for d in District.query.all()]
    form.CommuneID.choices = [(c.CommuneID, c.Name) for c in Commune.query.all()]
    form.VillageID.choices = [(v.VillageID, v.Name) for v in Village.query.all()]

    if form.validate_on_submit():
        address.Home = form.Home.data
        address.Street = form.Street.data
        address.ProvinceID = form.ProvinceID.data
        address.DistrictID = form.DistrictID.data
        address.CommuneID = form.CommuneID.data
        address.VillageID = form.VillageID.data
        db.session.commit()
        flash('Address updated successfully!', 'success')
        return redirect(url_for('location.manage_addresses'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Address.query.paginate(page=page, per_page=per_page, error_out=False)
    addresses = pagination.items

    flash('Failed to update address. Please check your input.', 'danger')
    return render_template(
        'locations/addresses.html',
        form=form,
        addresses=addresses,
        per_page=per_page,
        prev_url=url_for('location.manage_addresses', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None,
        next_url=url_for('location.manage_addresses', page=pagination.next_num, per_page=per_page) if pagination.has_next else None,
        edit_error_id=id
    )


@location_bp.route('/addresses/delete/<int:id>', methods=['POST'])
@login_required
def delete_address(id):
    address = Address.query.get_or_404(id)
    try:
        db.session.delete(address)
        db.session.commit()
        flash('Address deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this address because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_addresses'))