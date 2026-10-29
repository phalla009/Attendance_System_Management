from extensions import db
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from forms.location_form import CommuneForm
from models.location import Commune, District
from . import location_bp


@location_bp.route('/communes', methods=['GET', 'POST'])
@login_required
def manage_communes():
    form = CommuneForm()
    form.DistrictID.choices = [(d.DistrictID, d.Name) for d in District.query.all()]
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
    elif request.method == 'POST':
        flash('Please correct the errors in the form.', 'danger')

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
@login_required
def edit_commune(id):
    commune = Commune.query.get_or_404(id)
    form = CommuneForm()
    form.DistrictID.choices = [(d.DistrictID, d.Name) for d in District.query.all()]

    if form.validate_on_submit():
        commune.Name = form.Name.data
        commune.DistrictID = form.DistrictID.data
        db.session.commit()
        flash('Commune updated successfully!', 'success')
        return redirect(url_for('location.manage_communes'))
    elif request.method == 'POST':
        flash('Please correct the errors in the form.', 'danger')

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
@login_required
def delete_commune(id):
    commune = Commune.query.get_or_404(id)
    try:
        db.session.delete(commune)
        db.session.commit()
        flash('Commune deleted successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this commune because it is being used by other records!', 'danger')
    return redirect(url_for('location.manage_communes'))