from flask import Blueprint
location_bp = Blueprint('location', __name__, url_prefix='/location')
from . import provinces, districts, communes, villages, addresses