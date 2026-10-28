from flask import render_template
from flask_login import login_required

from models.academic import Class, Group, Session, Subject
from . import academic_bp


@academic_bp.route('/index')
@login_required
def index():
    return render_template(
        'academic/index.html',
        active_page='index',
        total_sessions=Session.query.count(),
        total_classes=Class.query.count(),
        total_groups=Group.query.count(),
        total_subjects=Subject.query.count()
    )