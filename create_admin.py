#!/usr/bin/env python3
"""
Script to create an initial admin user for the TEC Attendance Tracker
"""

from app import app, db, User
from datetime import datetime

def create_admin_user():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Check if admin user already exists
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            print(f"✅ Admin user '{admin_user.username}' already exists!")
            print(f"📧 Email: {admin_user.email}")
            print("🌐 Access the application at: http://127.0.0.1:5000")
            return

        # Check if any users exist
        if User.query.count() > 0:
            print("⚠️  Users exist but no admin found. Promoting first user to admin...")
            first_user = User.query.first()
            first_user.is_admin = True
            db.session.commit()
            print(f"✅ User '{first_user.username}' promoted to admin!")
            print("🌐 Access the application at: http://127.0.0.1:5000")
            return

        print("🔧 Creating initial admin user...")

        # Create admin user
        admin = User(
            username='admin',
            email='admin@tecattendance.local',
            is_admin=True
        )
        admin.set_password('admin123')  # Change this password!

        db.session.add(admin)
        db.session.commit()

        print("✅ Initial admin user created successfully!")
        print("📧 Username: admin")
        print("🔑 Password: admin123")
        print("⚠️  IMPORTANT: Change this password immediately after first login!")
        print("🔐 Self-registration is now disabled - only admins can create users")
        print("🌐 Access the application at: http://127.0.0.1:5000")

if __name__ == '__main__':
    create_admin_user()
