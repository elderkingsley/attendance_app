from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    attendances = db.relationship('Attendance', backref='meeting', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Meeting {self.name}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    men_count = db.Column(db.Integer, nullable=False, default=0)
    women_count = db.Column(db.Integer, nullable=False, default=0)
    children_count = db.Column(db.Integer, nullable=False, default=0)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)

    @property
    def total_count(self):
        return self.men_count + self.women_count + self.children_count

    def __repr__(self):
        return f'<Attendance {self.total_count} people>'

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')

            flash('Login successful!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Registration removed - only admins can create users through admin panel

# Admin Panel Routes
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    users = User.query.order_by(User.created_at.desc()).all()
    total_meetings = Meeting.query.count()
    total_attendance_records = Attendance.query.count()

    return render_template('admin_panel.html',
                         users=users,
                         total_meetings=total_meetings,
                         total_attendance_records=total_attendance_records)

@app.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
def admin_create_user():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        is_admin = 'is_admin' in request.form

        # Validation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('admin_create_user.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('admin_create_user.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('admin_create_user.html')

        # Create new user
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(f'User "{username}" created successfully!', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('admin_create_user.html')

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_panel'))

    # Prevent deleting the last admin
    if user.is_admin and User.query.filter_by(is_admin=True).count() <= 1:
        flash('Cannot delete the last admin user.', 'danger')
        return redirect(url_for('admin_panel'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'User "{username}" deleted successfully.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def admin_toggle_user_admin(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    # Prevent admin from removing their own admin status
    if user.id == current_user.id:
        flash('You cannot modify your own admin status.', 'danger')
        return redirect(url_for('admin_panel'))

    # Prevent removing admin status from the last admin
    if user.is_admin and User.query.filter_by(is_admin=True).count() <= 1:
        flash('Cannot remove admin status from the last admin user.', 'danger')
        return redirect(url_for('admin_panel'))

    user.is_admin = not user.is_admin
    db.session.commit()

    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for user "{user.username}".', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
def admin_reset_password(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('admin_reset_password.html', user=user)

        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('admin_reset_password.html', user=user)

        user.set_password(new_password)
        db.session.commit()

        flash(f'Password reset successfully for user "{user.username}".', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('admin_reset_password.html', user=user)

# Main Routes
@app.route('/')
@login_required
def index():
    recent_meetings = Meeting.query.order_by(Meeting.date.desc()).limit(5).all()
    return render_template('index.html', recent_meetings=recent_meetings)

@app.route('/meetings')
@login_required
def meetings():
    all_meetings = Meeting.query.order_by(Meeting.date.desc()).all()
    return render_template('meetings.html', meetings=all_meetings)

@app.route('/meeting/new', methods=['GET', 'POST'])
@login_required
def new_meeting():
    if request.method == 'POST':
        meeting = Meeting(
            name=request.form['name'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'),
            location=request.form.get('location', ''),
            description=request.form.get('description', '')
        )
        db.session.add(meeting)
        db.session.commit()
        return redirect(url_for('meeting_detail', id=meeting.id))
    
    return render_template('new_meeting.html')

@app.route('/meeting/<int:id>')
@login_required
def meeting_detail(id):
    meeting = Meeting.query.get_or_404(id)
    attendances = Attendance.query.filter_by(meeting_id=id).order_by(Attendance.recorded_at.desc()).all()
    return render_template('meeting_detail.html', meeting=meeting, attendances=attendances)

@app.route('/meeting/<int:id>/attendance', methods=['POST'])
@login_required
def record_attendance(id):
    meeting = Meeting.query.get_or_404(id)
    
    attendance = Attendance(
        meeting_id=id,
        men_count=int(request.form.get('men_count', 0)),
        women_count=int(request.form.get('women_count', 0)),
        children_count=int(request.form.get('children_count', 0)),
        notes=request.form.get('notes', '')
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return redirect(url_for('meeting_detail', id=id))

@app.route('/api/meetings/<int:id>/stats')
@login_required
def meeting_stats(id):
    meeting = Meeting.query.get_or_404(id)
    attendances = Attendance.query.filter_by(meeting_id=id).all()

    if not attendances:
        return jsonify({
            'total_records': 0,
            'average_attendance': 0,
            'total_men': 0,
            'total_women': 0,
            'total_children': 0
        })

    total_men = sum(a.men_count for a in attendances)
    total_women = sum(a.women_count for a in attendances)
    total_children = sum(a.children_count for a in attendances)
    total_people = total_men + total_women + total_children

    return jsonify({
        'total_records': len(attendances),
        'average_attendance': total_people / len(attendances) if attendances else 0,
        'total_men': total_men,
        'total_women': total_women,
        'total_children': total_children,
        'total_people': total_people
    })

@app.route('/meeting/<int:id>/export')
@login_required
def export_meeting_data(id):
    meeting = Meeting.query.get_or_404(id)
    attendances = Attendance.query.filter_by(meeting_id=id).order_by(Attendance.recorded_at.desc()).all()

    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Meeting Name',
        'Meeting Date',
        'Record Date',
        'Men Count',
        'Women Count',
        'Children Count',
        'Total Count',
        'Notes'
    ])

    # Write data rows
    for attendance in attendances:
        writer.writerow([
            meeting.name,
            meeting.date.strftime('%Y-%m-%d %H:%M'),
            attendance.recorded_at.strftime('%Y-%m-%d %H:%M'),
            attendance.men_count,
            attendance.women_count,
            attendance.children_count,
            attendance.total_count,
            attendance.notes or ''
        ])

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{meeting.name}_attendance.csv"'

    return response

@app.route('/export/all')
@login_required
def export_all_data():
    meetings = Meeting.query.order_by(Meeting.date.desc()).all()

    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Meeting Name',
        'Meeting Date',
        'Meeting Location',
        'Record Date',
        'Men Count',
        'Women Count',
        'Children Count',
        'Total Count',
        'Notes'
    ])

    # Write data rows
    for meeting in meetings:
        for attendance in meeting.attendances:
            writer.writerow([
                meeting.name,
                meeting.date.strftime('%Y-%m-%d %H:%M'),
                meeting.location or '',
                attendance.recorded_at.strftime('%Y-%m-%d %H:%M'),
                attendance.men_count,
                attendance.women_count,
                attendance.children_count,
                attendance.total_count,
                attendance.notes or ''
            ])

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename="all_attendance_data.csv"'

    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
