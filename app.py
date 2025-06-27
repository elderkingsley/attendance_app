from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
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

# Routes
@app.route('/')
def index():
    recent_meetings = Meeting.query.order_by(Meeting.date.desc()).limit(5).all()
    return render_template('index.html', recent_meetings=recent_meetings)

@app.route('/meetings')
def meetings():
    all_meetings = Meeting.query.order_by(Meeting.date.desc()).all()
    return render_template('meetings.html', meetings=all_meetings)

@app.route('/meeting/new', methods=['GET', 'POST'])
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
def meeting_detail(id):
    meeting = Meeting.query.get_or_404(id)
    attendances = Attendance.query.filter_by(meeting_id=id).order_by(Attendance.recorded_at.desc()).all()
    return render_template('meeting_detail.html', meeting=meeting, attendances=attendances)

@app.route('/meeting/<int:id>/attendance', methods=['POST'])
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
