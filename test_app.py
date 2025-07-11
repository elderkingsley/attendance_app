#!/usr/bin/env python3
"""
Basic tests for the attendance application
"""

import unittest
import tempfile
import os
from app import app, db, Meeting, Attendance, User
from datetime import datetime

class AttendanceAppTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app = app.test_client()

        with app.app_context():
            db.create_all()
            # Create a test admin user
            self.test_user = User(username='testuser', email='test@example.com', is_admin=True)
            self.test_user.set_password('testpass')
            db.session.add(self.test_user)
            db.session.commit()
    
    def tearDown(self):
        """Clean up after each test method."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def login(self, username='testuser', password='testpass'):
        """Helper method to login a user."""
        return self.app.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def test_login_page(self):
        """Test that the login page loads correctly."""
        rv = self.app.get('/login')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'TEC Attendance Tracker', rv.data)
        self.assertIn(b'Please sign in', rv.data)

    def test_login_success(self):
        """Test successful login."""
        rv = self.login()
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'TEC Attendance Tracker', rv.data)

    def test_login_failure(self):
        """Test failed login with wrong credentials."""
        rv = self.login('wronguser', 'wrongpass')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Invalid username or password', rv.data)

    def test_home_page_requires_login(self):
        """Test that the home page requires login."""
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 302)  # Redirect to login

    def test_home_page_after_login(self):
        """Test that the home page loads correctly after login."""
        self.login()
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'TEC Attendance Tracker', rv.data)
    
    def test_meetings_page_requires_login(self):
        """Test that the meetings page requires login."""
        rv = self.app.get('/meetings')
        self.assertEqual(rv.status_code, 302)  # Redirect to login

    def test_meetings_page_after_login(self):
        """Test that the meetings page loads correctly after login."""
        self.login()
        rv = self.app.get('/meetings')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'All Meetings', rv.data)
    
    def test_new_meeting_page_requires_login(self):
        """Test that the new meeting page requires login."""
        rv = self.app.get('/meeting/new')
        self.assertEqual(rv.status_code, 302)  # Redirect to login

    def test_new_meeting_page_after_login(self):
        """Test that the new meeting page loads correctly after login."""
        self.login()
        rv = self.app.get('/meeting/new')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Create New Meeting', rv.data)

    def test_create_meeting(self):
        """Test creating a new meeting."""
        self.login()  # Login first
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
        self.login()  # Login first
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
        self.login()  # Login first
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
        self.login()  # Login first
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

    def test_admin_panel_access(self):
        """Test that admin panel is accessible to admin users."""
        self.login()  # Login as admin
        rv = self.app.get('/admin')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Admin Panel', rv.data)
        self.assertIn(b'User Management', rv.data)

    def test_admin_create_user(self):
        """Test admin user creation functionality."""
        self.login()  # Login as admin
        with app.app_context():
            user_data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'newpass123',
                'confirm_password': 'newpass123'
            }

            rv = self.app.post('/admin/users/new', data=user_data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)

            # Check that user was created
            new_user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(new_user)
            self.assertEqual(new_user.email, 'newuser@example.com')
            self.assertFalse(new_user.is_admin)  # Should not be admin by default

if __name__ == '__main__':
    unittest.main()
