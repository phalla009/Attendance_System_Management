from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.location_form import VillageForm
from models.location import Commune, Village
from . import location_bp


@location_bp.route('/villages', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def delete_village(id):
    village = Village.query.get_or_404(id)
    try:
        db.session.delete(village)
        db.session.commit()
        flash('Village deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this village because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_villages'))