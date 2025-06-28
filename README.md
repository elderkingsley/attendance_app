# TEC Attendance Tracker

A web-based application for collecting and tracking attendance at meetings, specifically designed to count men, women, and children separately.

## Features

- **🔐 User Authentication**: Secure login system with username/password
- **👥 Admin-Controlled User Management**: Only administrators can create and manage user accounts
- **📅 Meeting Management**: Create and manage different meetings/events
- **📊 Attendance Recording**: Record attendance counts for men, women, and children
- **📈 Historical Data**: View attendance history and statistics
- **📱 Responsive Design**: Works on desktop and mobile devices
- **⚡ Real-time Calculations**: Automatic total calculations and statistics
- **📤 Data Export**: Export attendance data to CSV format

## Technology Stack

- **Backend**: Python Flask with SQLAlchemy
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Styling**: Bootstrap 5 + Custom CSS

## Installation

1. **Clone or download the project**
   ```bash
   cd attendance_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in browser**
   Navigate to `http://127.0.0.1:5000`

5. **Create initial admin account**
   - Run `python create_admin.py` to create the first administrator
   - Or if users already exist, the first user will be promoted to admin

## Authentication

### First Time Setup
1. Run `python create_admin.py` to create the initial admin account
2. Navigate to `http://127.0.0.1:5000`
3. Login with the admin credentials
4. Use the Admin Panel to create additional user accounts

### Login Credentials
- **Username**: Your chosen username
- **Password**: Your chosen password
- **Remember Me**: Optional checkbox to stay logged in

### User Roles
- **Admin**: Can access all features, manage users, and access the admin panel
- **Regular User**: Can access all attendance tracking features (meetings, recording, statistics, export)

## Usage

### Creating a Meeting

1. Click "New Meeting" from the navigation or home page
2. Fill in the meeting details:
   - **Name**: e.g., "Sunday Service", "Bible Study"
   - **Date & Time**: When the meeting occurs
   - **Location**: Optional venue information
   - **Description**: Optional additional details

### Recording Attendance

1. Navigate to a meeting's detail page
2. Use the attendance form to enter counts:
   - **Men**: Number of adult men present
   - **Women**: Number of adult women present
   - **Children**: Number of children present
3. Add optional notes if needed
4. Click "Record Attendance"

### Viewing Statistics

Each meeting page shows:
- Total number of attendance records
- Average attendance across all records
- Breakdown by men, women, and children
- Historical attendance data in table format

## Database Schema

### Meeting Table
- `id`: Primary key
- `name`: Meeting name
- `date`: Meeting date and time
- `location`: Optional location
- `description`: Optional description

### Attendance Table
- `id`: Primary key
- `meeting_id`: Foreign key to Meeting
- `men_count`: Number of men
- `women_count`: Number of women
- `children_count`: Number of children
- `recorded_at`: Timestamp when recorded
- `notes`: Optional notes

## API Endpoints

- `GET /`: Home page with recent meetings
- `GET /meetings`: List all meetings
- `GET /meeting/new`: Create new meeting form
- `POST /meeting/new`: Create new meeting
- `GET /meeting/<id>`: Meeting detail page
- `POST /meeting/<id>/attendance`: Record attendance
- `GET /api/meetings/<id>/stats`: Get meeting statistics (JSON)

## Future Enhancements

- Export data to CSV/Excel
- Advanced reporting and analytics
- User authentication and permissions
- Email notifications
- Mobile app
- Integration with calendar systems

## Development

The application uses Flask's development server. For production deployment:

1. Use a production WSGI server (e.g., Gunicorn)
2. Configure a production database
3. Set up proper environment variables
4. Enable HTTPS
5. Configure proper logging

## License

This project is open source and available under the MIT License.
