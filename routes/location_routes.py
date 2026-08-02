from extensions import db
from flask import Blueprint, flash, redirect, render_template, url_for
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

    provinces = Province.query.all()
    return render_template(
        'locations/provinces.html', form=form, provinces=provinces
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

    provinces = Province.query.all()
    flash('Failed to update province. Please check your input.', 'danger')
    return render_template(
        'locations/provinces.html',
        form=form,
        provinces=provinces,
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

    districts = District.query.all()
    return render_template(
        'locations/districts.html', form=form, districts=districts
    )

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

    communes = Commune.query.all()
    return render_template('locations/communes.html', form=form, communes=communes)

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

    villages = Village.query.all()
    return render_template('locations/villages.html', form=form, villages=villages)

# ==================== ADDRESSES ROUTES ====================
@location_bp.route('/addresses', methods=['GET', 'POST'])
def manage_addresses():
    form = AddressForm()
    form.ProvinceID.choices = [
        (p.ProvinceID, p.Name) for p in Province.query.all()
    ]
    form.DistrictID.choices = [
        (d.DistrictID, d.Name) for d in District.query.all()
    ]
    form.CommuneID.choices = [
        (c.CommuneID, c.Name) for c in Commune.query.all()
    ]
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

    addresses = Address.query.all()
    return render_template(
        'locations/addresses.html', form=form, addresses=addresses
    )