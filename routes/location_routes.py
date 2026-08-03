from extensions import db
from flask import Blueprint, flash, redirect, render_template, url_for, request
from forms.location_form import (
    AddressForm,
    CommuneForm,
    DistrictForm,
    ProvinceForm,
    VillageForm,
)
from models.location import Address, Commune, District, Province, Village

location_bp = Blueprint('location', __name__, url_prefix='/location')

# ==================== PROVINCES ROUTES ====================
@location_bp.route('/provinces', methods=['GET', 'POST'])
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
def delete_province(id):
    province = Province.query.get_or_404(id)
    try:
        db.session.delete(province)
        db.session.commit()
        flash('Province deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this province because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_provinces'))


# ==================== DISTRICTS ROUTES ====================
@location_bp.route('/districts', methods=['GET', 'POST'])
def manage_districts():
    form = DistrictForm()
    form.ProvinceID.choices = [
        (p.ProvinceID, p.Name) for p in Province.query.all()
    ]
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
def edit_district(id):
    district = District.query.get_or_404(id)
    form = DistrictForm()
    form.ProvinceID.choices = [
        (p.ProvinceID, p.Name) for p in Province.query.all()
    ]

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
def delete_district(id):
    district = District.query.get_or_404(id)
    try:
        db.session.delete(district)
        db.session.commit()
        flash('District deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this district because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_districts'))


# ==================== COMMUNES ROUTES ====================
@location_bp.route('/communes', methods=['GET', 'POST'])
def manage_communes():
    form = CommuneForm()
    form.DistrictID.choices = [
        (d.DistrictID, d.Name) for d in District.query.all()
    ]
    if form.validate_on_submit():
        commune = Commune(
            Code=form.Code.data,
            Name=form.Name.data,
            DistrictID=form.DistrictID.data,
        )
        db.session.add(commune)
        db.session.commit()
        flash('Commune added successfully!', 'success')
        return redirect(url_for('location.manage_communes'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Commune.query.paginate(page=page, per_page=per_page, error_out=False)
    communes = pagination.items

    prev_url = url_for('location.manage_communes', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None
    next_url = url_for('location.manage_communes', page=pagination.next_num, per_page=per_page) if pagination.has_next else None

    return render_template(
        'locations/communes.html',
        form=form,
        communes=communes,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url
    )

@location_bp.route('/communes/edit/<int:id>', methods=['POST'])
def edit_commune(id):
    commune = Commune.query.get_or_404(id)
    form = CommuneForm()
    form.DistrictID.choices = [
        (d.DistrictID, d.Name) for d in District.query.all()
    ]

    if form.validate_on_submit():
        commune.Name = form.Name.data
        commune.DistrictID = form.DistrictID.data
        db.session.commit()
        flash('Commune updated successfully!', 'success')
        return redirect(url_for('location.manage_communes'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Commune.query.paginate(page=page, per_page=per_page, error_out=False)
    communes = pagination.items

    flash('Failed to update commune. Please check your input.', 'danger')
    return render_template(
        'locations/communes.html',
        form=form,
        communes=communes,
        per_page=per_page,
        prev_url=url_for('location.manage_communes', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None,
        next_url=url_for('location.manage_communes', page=pagination.next_num, per_page=per_page) if pagination.has_next else None,
        edit_error_id=id
    )

@location_bp.route('/communes/delete/<int:id>', methods=['POST'])
def delete_commune(id):
    commune = Commune.query.get_or_404(id)
    try:
        db.session.delete(commune)
        db.session.commit()
        flash('Commune deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this commune because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_communes'))


# ==================== VILLAGES ROUTES ====================
@location_bp.route('/villages', methods=['GET', 'POST'])
def manage_villages():
    form = VillageForm()
    form.CommuneID.choices = [(c.CommuneID, c.Name) for c in Commune.query.all()]
    if form.validate_on_submit():
        village = Village(
            Code=form.Code.data, Name=form.Name.data, CommuneID=form.CommuneID.data
        )
        db.session.add(village)
        db.session.commit()
        flash('Village added successfully!', 'success')
        return redirect(url_for('location.manage_villages'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Village.query.paginate(page=page, per_page=per_page, error_out=False)
    villages = pagination.items

    prev_url = url_for('location.manage_villages', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None
    next_url = url_for('location.manage_villages', page=pagination.next_num, per_page=per_page) if pagination.has_next else None

    return render_template(
        'locations/villages.html',
        form=form,
        villages=villages,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url
    )

@location_bp.route('/villages/edit/<int:id>', methods=['POST'])
def edit_village(id):
    village = Village.query.get_or_404(id)
    form = VillageForm()
    form.CommuneID.choices = [(c.CommuneID, c.Name) for c in Commune.query.all()]

    if form.validate_on_submit():
        village.Name = form.Name.data
        village.CommuneID = form.CommuneID.data
        db.session.commit()
        flash('Village updated successfully!', 'success')
        return redirect(url_for('location.manage_villages'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Village.query.paginate(page=page, per_page=per_page, error_out=False)
    villages = pagination.items

    flash('Failed to update village. Please check your input.', 'danger')
    return render_template(
        'locations/villages.html',
        form=form,
        villages=villages,
        per_page=per_page,
        prev_url=url_for('location.manage_villages', page=pagination.prev_num, per_page=per_page) if pagination.has_prev else None,
        next_url=url_for('location.manage_villages', page=pagination.next_num, per_page=per_page) if pagination.has_next else None,
        edit_error_id=id
    )

@location_bp.route('/villages/delete/<int:id>', methods=['POST'])
def delete_village(id):
    village = Village.query.get_or_404(id)
    try:
        db.session.delete(village)
        db.session.commit()
        flash('Village deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this village because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_villages'))


# ==================== ADDRESSES ROUTES ====================
@location_bp.route('/addresses', methods=['GET', 'POST'])
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
def delete_address(id):
    address = Address.query.get_or_404(id)
    try:
        db.session.delete(address)
        db.session.commit()
        flash('Address deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete this address because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_addresses'))