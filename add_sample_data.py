#!/usr/bin/env python3
"""
Script to add sample data to the attendance application for testing
"""

from app import app, db, Meeting, Attendance
from datetime import datetime, timedelta

def add_sample_data():
    with app.app_context():
        # Create sample meetings
        meetings_data = [
            {
                'name': 'Sunday Morning Service',
                'date': datetime.now() - timedelta(days=7),
                'location': 'Main Sanctuary',
                'description': 'Weekly Sunday morning worship service'
            },
            {
                'name': 'Wednesday Bible Study',
                'date': datetime.now() - timedelta(days=4),
                'location': 'Fellowship Hall',
                'description': 'Midweek Bible study and prayer'
            },
            {
                'name': 'Youth Meeting',
                'date': datetime.now() - timedelta(days=2),
                'location': 'Youth Room',
                'description': 'Monthly youth gathering'
            }
        ]
        
        for meeting_data in meetings_data:
            # Check if meeting already exists
            existing = Meeting.query.filter_by(name=meeting_data['name']).first()
            if not existing:
                meeting = Meeting(**meeting_data)
                db.session.add(meeting)
                db.session.commit()
                
                # Add sample attendance records for each meeting
                attendance_records = [
                    {'men_count': 25, 'women_count': 30, 'children_count': 15, 'notes': 'Good attendance'},
                    {'men_count': 22, 'women_count': 28, 'children_count': 12, 'notes': 'Slightly lower than usual'},
                    {'men_count': 28, 'women_count': 32, 'children_count': 18, 'notes': 'Great turnout!'}
                ]
                
                for i, record_data in enumerate(attendance_records):
                    attendance = Attendance(
                        meeting_id=meeting.id,
                        recorded_at=meeting.date + timedelta(minutes=i*30),  # Stagger the records
                        **record_data
                    )
                    db.session.add(attendance)
                
                db.session.commit()
                print(f"Added meeting: {meeting.name} with {len(attendance_records)} attendance records")
            else:
                print(f"Meeting '{meeting_data['name']}' already exists, skipping...")
        
        print("\nSample data added successfully!")
        print("You can now test the application with realistic data.")

if __name__ == '__main__':
    add_sample_data()
