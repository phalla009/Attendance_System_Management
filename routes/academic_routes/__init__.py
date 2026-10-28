from flask import Blueprint

academic_bp = Blueprint('academic', __name__, url_prefix='/academic')

# Import submodules AFTER creating the blueprint so their routes get registered
from . import index, sessions, classes, groups, subjects  # noqa: E402,F401