# Authentication System - TEC Attendance Tracker

## 🔐 Security Features

The TEC Attendance Tracker now includes a comprehensive authentication system to secure your attendance data.

### **Security Measures Implemented:**
- ✅ **Password Hashing**: All passwords are securely hashed using Werkzeug's security functions
- ✅ **Session Management**: Secure session handling with Flask-Login
- ✅ **CSRF Protection**: Built-in protection against cross-site request forgery
- ✅ **Login Required**: All attendance features require authentication
- ✅ **User Roles**: Admin and regular user permissions

## 👥 User Management

### **User Registration**
1. Navigate to the registration page
2. Fill in required information:
   - **Username**: 3-20 characters, must be unique
   - **Email**: Valid email address, must be unique
   - **Password**: Minimum 6 characters
   - **Confirm Password**: Must match the password
3. Click "Create Account"
4. **First user automatically becomes admin**

### **User Login**
1. Navigate to the login page
2. Enter your credentials:
   - **Username**: Your registered username
   - **Password**: Your password
   - **Remember Me**: Optional - keeps you logged in longer
3. Click "Sign In"

### **User Logout**
- Click on your username in the navigation bar
- Select "Logout" from the dropdown menu

## 🔑 Default Admin Account

If you need to create an admin account manually, you can use the provided script:

```bash
python create_admin.py
```

**Default Credentials** (if created via script):
- **Username**: `admin`
- **Password**: `admin123`
- ⚠️ **IMPORTANT**: Change this password immediately after first login!

## 👑 User Roles & Permissions

### **Administrator**
- ✅ Full access to all features
- ✅ Can view all meetings and attendance data
- ✅ Can export all data
- ✅ Future: User management capabilities

### **Regular User**
- ✅ Can create and manage meetings
- ✅ Can record attendance
- ✅ Can view attendance history and statistics
- ✅ Can export meeting data

## 🛡️ Security Best Practices

### **For Administrators:**
1. **Change Default Passwords**: Always change default passwords immediately
2. **Strong Passwords**: Use passwords with at least 8 characters, including numbers and symbols
3. **Regular Updates**: Keep the application updated
4. **Secure Environment**: Run on HTTPS in production

### **For Users:**
1. **Unique Passwords**: Don't reuse passwords from other services
2. **Logout**: Always logout when using shared computers
3. **Report Issues**: Report any suspicious activity to administrators

## 🔧 Technical Implementation

### **Database Schema**
```sql
User Table:
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash (Hashed)
- is_admin (Boolean)
- created_at (Timestamp)
- last_login (Timestamp)
```

### **Authentication Flow**
1. User submits login credentials
2. System verifies username exists
3. Password is checked against stored hash
4. Session is created for valid users
5. User is redirected to requested page

### **Session Management**
- Sessions are managed by Flask-Login
- "Remember Me" extends session duration
- Sessions expire after inactivity
- Secure session cookies are used

## 🚀 Getting Started

### **First Time Setup:**
1. Start the application: `python app.py`
2. Open browser: `http://127.0.0.1:5000`
3. You'll be redirected to the login page
4. Click "Register here" to create your account
5. Fill in your information and submit
6. You'll be redirected to login
7. Sign in with your new credentials
8. Start using the attendance tracker!

### **Subsequent Logins:**
1. Navigate to `http://127.0.0.1:5000`
2. Enter your username and password
3. Click "Sign In"
4. Access all attendance tracking features

## 🔍 Troubleshooting

### **Can't Login?**
- ✅ Check username spelling (case-sensitive)
- ✅ Verify password is correct
- ✅ Ensure account exists (try registration if new user)
- ✅ Clear browser cache/cookies

### **Forgot Password?**
- Currently: Contact administrator for password reset
- Future: Self-service password reset feature planned

### **Registration Issues?**
- ✅ Username must be unique (3-20 characters)
- ✅ Email must be unique and valid format
- ✅ Password must be at least 6 characters
- ✅ Confirm password must match

### **Session Issues?**
- ✅ Try logging out and back in
- ✅ Clear browser cookies
- ✅ Check if session expired

## 📱 Mobile Authentication

The authentication system is fully mobile-responsive:
- ✅ Touch-friendly login forms
- ✅ Proper mobile keyboard types
- ✅ Responsive design for all screen sizes
- ✅ Auto-zoom prevention on iOS

## 🔮 Future Enhancements

Planned authentication features:
- 📧 Email verification for new accounts
- 🔄 Password reset via email
- 👥 Advanced user management for admins
- 🔐 Two-factor authentication (2FA)
- 📊 User activity logging
- ⏰ Session timeout configuration

The authentication system provides a solid foundation for secure attendance tracking while maintaining ease of use!
