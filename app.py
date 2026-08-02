from extensions import db
from flask import Flask, render_template
from flask_migrate import Migrate
import models

# នាំចូល Blueprints ទាំងអស់ពីថត routes
from routes import academic_bp, attendance_bp, location_bp, user_bp

# Import ម៉ូឌែលទីតាំងសម្រាប់ធ្វើការ query ចំនួនសរុប (Total Counts)
from models.location import Commune, District, Province, Village

# Import ម៉ូឌែល User ពី models.user
import models.user as user_models

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-super-secret-key-here'

db.init_app(app)
migrate = Migrate(app, db)

# ចុះឈ្មោះ Blueprints ទាំងអស់
app.register_blueprint(academic_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(location_bp, url_prefix='/location')
app.register_blueprint(user_bp)


@app.route('/api')
def api():
    return 'Attendance System Database API is running!'


# ទំព័រដើម (Home Dashboard) សម្រាប់ផ្នែក Academic
@app.route('/academic/index')
def index():
    total_sessions = (
        models.SessionModel.query.count()
        if hasattr(models, 'SessionModel')
        else 0
    )
    total_classes = (
        models.ClassModel.query.count() if hasattr(models, 'ClassModel') else 0
    )
    total_groups = (
        models.GroupModel.query.count() if hasattr(models, 'GroupModel') else 0
    )
    total_subjects = (
        models.SubjectModel.query.count() if hasattr(models, 'SubjectModel') else 0
    )

    return render_template(
        'academic/index.html',
        active_page='index',
        total_sessions=total_sessions,
        total_classes=total_classes,
        total_groups=total_groups,
        total_subjects=total_subjects,
    )


# ទំព័រដើមសម្រាប់ផ្នែក User Management (Dashboard)
@app.route('/user/index')
def user_index():
    total_profiles = (
        user_models.UserProfile.query.count()
        if hasattr(user_models, 'UserProfile')
        else 0
    )
    total_usertypes = (
        user_models.UserType.query.count()
        if hasattr(user_models, 'UserType')
        else 0
    )
    total_contacts = (
        user_models.ContactNo.query.count()
        if hasattr(user_models, 'ContactNo')
        else 0
    )

    # ត្រួតពិនិត្យ Address ថាតើស្ថិតក្នុង models.user ឬ models.location
    total_addresses = 0
    if hasattr(user_models, 'Address'):
        total_addresses = user_models.Address.query.count()
    elif hasattr(models, 'Address'):
        total_addresses = models.Address.query.count()

    return render_template(
        'users/index.html',
        active_page='user_index',
        total_profiles=total_profiles,
        total_usertypes=total_usertypes,
        total_contacts=total_contacts,
        total_addresses=total_addresses,
    )


# ទំព័រដើមសម្រាប់ផ្នែក Location Management
@app.route('/location/index')
def location_index():
    total_provinces = Province.query.count() if 'Province' in globals() else 0
    total_districts = District.query.count() if 'District' in globals() else 0
    total_communes = Commune.query.count() if 'Commune' in globals() else 0
    total_villages = Village.query.count() if 'Village' in globals() else 0

    return render_template(
        'locations/index.html',
        active_page='location_index',
        total_provinces=total_provinces,
        total_districts=total_districts,
        total_communes=total_communes,
        total_villages=total_villages,
    )


# ទំព័រ Analytics / Dashboard ផ្លាស់ប្តូរមក path នេះវិញ
@app.route('/dashboard')
def dashboard():
    return render_template(
        'attendance/dashboard.html',
        active_page='dashboard',
        total_users=120,
        present_count=105,
        present_rate=87.5,
        late_count=10,
        absent_count=5,
    )
@app.route('/')
def login():
    return render_template(
        'users/login.html',
        active_page='login',

    )

if __name__ == '__main__':
    app.run(debug=True)