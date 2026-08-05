from extensions import db
from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
import models

# Import all Blueprints from the routes package
from routes import academic_bp, attendance_bp, location_bp, user_bp

# Import location models for total count queries
from models.location import Commune, District, Province, Village

# Import User models from models.user
import models.user as user_models

# Import Attendance models for dashboard metrics query if needed
from models.attendance import Attendance

# Import Flask-Login
from flask_login import LoginManager, login_required
from datetime import date, datetime
from sqlalchemy import extract

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-super-secret-key-here'

db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-Login and bind it explicitly to the app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Name of the login route function
app.login_manager = login_manager  # Explicitly attach login_manager attribute to the Flask app instance


@login_manager.user_loader
def load_user(user_id):
    if hasattr(user_models, 'User'):
        return user_models.User.query.get(int(user_id))
    return user_models.UserProfile.query.get(int(user_id))


# Register all Blueprints
app.register_blueprint(academic_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(location_bp, url_prefix='/location')
app.register_blueprint(user_bp)


@app.route('/api')
def api():
    return 'Attendance System Database API is running!'


# Academic Home Dashboard
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


# User Management Home Dashboard
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

    # ➕ បន្ថែមការរាប់ចំនួន Teacher (TypeID = 1) និង Student (TypeID = 2)
    total_teachers = (
        user_models.UserProfile.query.filter_by(TypeID=1).count()
        if hasattr(user_models, 'UserProfile')
        else 0
    )
    total_students = (
        user_models.UserProfile.query.filter_by(TypeID=2).count()
        if hasattr(user_models, 'UserProfile')
        else 0
    )

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
        total_teachers=total_teachers,
        total_students=total_students,
    )


# Location Management Home Dashboard
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


# Analytics / Main Root Dashboard Route with Real Data
@app.route('/dashboard')
def dashboard():
    today = date.today()

    total_users = user_models.UserProfile.query.count() if hasattr(user_models.UserProfile, 'query') else 0

    present_count = Attendance.query.filter(
        Attendance.Status == 'Present',
        db.func.date(Attendance.Date) == today
    ).count() if hasattr(Attendance, 'query') else 0

    late_count = Attendance.query.filter(
        Attendance.Status == 'Late',
        db.func.date(Attendance.Date) == today
    ).count() if hasattr(Attendance, 'Status') else 0

    absent_count = Attendance.query.filter(
        Attendance.Status == 'Absent',
        db.func.date(Attendance.Date) == today
    ).count() if hasattr(Attendance, 'Status') else 0

    present_rate = round((present_count / total_users * 100) if total_users > 0 else 0, 1)

    current_year = datetime.now().year
    monthly_counts = []
    for month in range(1, 13):
        count = Attendance.query.filter(
            extract('year', Attendance.Date) == current_year,
            extract('month', Attendance.Date) == month,
            Attendance.Status == 'Present'
        ).count() if hasattr(Attendance, 'query') else 0
        monthly_counts.append(count)

    time_slots = [8, 10, 12, 14, 16]
    hourly_counts = []
    for hour in time_slots:
        count = Attendance.query.filter(
            extract('hour', Attendance.Date) == hour
        ).count() if hasattr(Attendance, 'query') else 0
        hourly_counts.append(count)

    return render_template(
        'attendance/dashboard.html',
        active_page='dashboard',
        total_users=total_users or 0,
        present_count=present_count or 0,
        present_rate=present_rate or 0.0,
        late_count=late_count or 0,
        absent_count=absent_count or 0,
        monthly_counts=monthly_counts if monthly_counts else [0] * 12,
        hourly_counts=hourly_counts if hourly_counts else [0] * 5,
    )


# Direct Scan Route redirecting to active sessions
@app.route('/scan')
@login_required
def root_scan():
    return redirect(url_for('attendance.active_scan_sessions'))


@app.route('/')
def login():
    return render_template(
        'users/login.html',
        active_page='login',
    )


if __name__ == '__main__':
    app.run(debug=True)