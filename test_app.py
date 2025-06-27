#!/usr/bin/env python3
"""
Basic tests for the attendance application
"""

import unittest
import tempfile
import os
from app import app, db, Meeting, Attendance
from datetime import datetime

class AttendanceAppTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test method."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def test_home_page(self):
        """Test that the home page loads correctly."""
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Attendance Tracker', rv.data)
    
    def test_meetings_page(self):
        """Test that the meetings page loads correctly."""
        rv = self.app.get('/meetings')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'All Meetings', rv.data)
    
    def test_new_meeting_page(self):
        """Test that the new meeting page loads correctly."""
        rv = self.app.get('/meeting/new')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Create New Meeting', rv.data)
    
    def test_create_meeting(self):
        """Test creating a new meeting."""
        with app.app_context():
            meeting_data = {
                'name': 'Test Meeting',
                'date': '2024-01-01T10:00',
                'location': 'Test Location',
                'description': 'Test Description'
            }
            
            rv = self.app.post('/meeting/new', data=meeting_data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            
            # Check that meeting was created
            meeting = Meeting.query.filter_by(name='Test Meeting').first()
            self.assertIsNotNone(meeting)
            self.assertEqual(meeting.location, 'Test Location')
    
    def test_record_attendance(self):
        """Test recording attendance for a meeting."""
        with app.app_context():
            # Create a test meeting
            meeting = Meeting(
                name='Test Meeting',
                date=datetime.now(),
                location='Test Location'
            )
            db.session.add(meeting)
            db.session.commit()
            
            # Record attendance
            attendance_data = {
                'men_count': '10',
                'women_count': '15',
                'children_count': '5',
                'notes': 'Test attendance'
            }
            
            rv = self.app.post(f'/meeting/{meeting.id}/attendance', 
                             data=attendance_data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            
            # Check that attendance was recorded
            attendance = Attendance.query.filter_by(meeting_id=meeting.id).first()
            self.assertIsNotNone(attendance)
            self.assertEqual(attendance.men_count, 10)
            self.assertEqual(attendance.women_count, 15)
            self.assertEqual(attendance.children_count, 5)
            self.assertEqual(attendance.total_count, 30)
    
    def test_meeting_stats_api(self):
        """Test the meeting statistics API."""
        with app.app_context():
            # Create a test meeting with attendance
            meeting = Meeting(
                name='Test Meeting',
                date=datetime.now()
            )
            db.session.add(meeting)
            db.session.commit()
            
            attendance = Attendance(
                meeting_id=meeting.id,
                men_count=10,
                women_count=15,
                children_count=5
            )
            db.session.add(attendance)
            db.session.commit()
            
            # Test API endpoint
            rv = self.app.get(f'/api/meetings/{meeting.id}/stats')
            self.assertEqual(rv.status_code, 200)
            
            data = rv.get_json()
            self.assertEqual(data['total_records'], 1)
            self.assertEqual(data['total_people'], 30)
            self.assertEqual(data['total_men'], 10)
            self.assertEqual(data['total_women'], 15)
            self.assertEqual(data['total_children'], 5)
    
    def test_export_functionality(self):
        """Test CSV export functionality."""
        with app.app_context():
            # Create test data
            meeting = Meeting(
                name='Test Meeting',
                date=datetime.now()
            )
            db.session.add(meeting)
            db.session.commit()
            
            attendance = Attendance(
                meeting_id=meeting.id,
                men_count=10,
                women_count=15,
                children_count=5,
                notes='Test export'
            )
            db.session.add(attendance)
            db.session.commit()
            
            # Test export
            rv = self.app.get(f'/meeting/{meeting.id}/export')
            self.assertEqual(rv.status_code, 200)
            self.assertTrue(rv.content_type.startswith('text/csv'))
            self.assertIn(b'Test Meeting', rv.data)
            self.assertIn(b'10,15,5,30', rv.data)

if __name__ == '__main__':
    unittest.main()
