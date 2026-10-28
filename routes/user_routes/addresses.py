from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required
from extensions import db
from forms.user_form import AddressForm
from models.location import Address, Commune, District, Province, Village
from . import user_bp


@user_bp.route('/addresses', methods=['GET', 'POST'])
@login_required
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
    form.VillageID.choices = [
        (v.VillageID, v.Name) for v in Village.query.all()
    ]

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if request.method == 'POST':
        if session.get('user_type') != 'Teacher':
            flash('Access Denied! Only Teacher can add addresses.', 'danger')
            return redirect(url_for('user.manage_addresses'))

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
            return redirect(url_for('user.manage_addresses'))

    pagination = Address.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    addresses = pagination.items

    prev_url = (
        url_for('user.manage_addresses', page=pagination.prev_num, per_page=per_page)
        if pagination.has_prev
        else None
    )
    next_url = (
        url_for('user.manage_addresses', page=pagination.next_num, per_page=per_page)
        if pagination.has_next
        else None
    )

    return render_template(
        'users/addresses.html',
        form=form,
        addresses=addresses,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url,
    )


@user_bp.route('/addresses/edit/<int:id>', methods=['POST'])
@login_required
def edit_address(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can edit addresses.', 'danger')
        return redirect(url_for('user.manage_addresses'))

    address = Address.query.get_or_404(id)
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
    form.VillageID.choices = [
        (v.VillageID, v.Name) for v in Village.query.all()
    ]

    if form.validate_on_submit():
        address.Home = form.Home.data
        address.Street = form.Street.data
        address.ProvinceID = form.ProvinceID.data
        address.DistrictID = form.DistrictID.data
        address.CommuneID = form.CommuneID.data
        address.VillageID = form.VillageID.data

        db.session.commit()
        flash('Address updated successfully!', 'success')
        return redirect(url_for('user.manage_addresses'))

    flash('Failed to update address. Please check your inputs.', 'danger')
    return redirect(url_for('user.manage_addresses'))


@user_bp.route('/addresses/delete/<int:id>', methods=['POST'])
@login_required
def delete_address(id):
    if session.get('user_type') != 'Teacher':
        flash('Access Denied! Only Teacher can delete addresses.', 'danger')
        return redirect(url_for('user.manage_addresses'))

    address = Address.query.get_or_404(id)
    try:
        db.session.delete(address)
        db.session.commit()
        flash('Address deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash(
            'Cannot delete this address because it is linked to user'
            ' profiles!',
            'danger',
        )

    return redirect(url_for('user.manage_addresses'))