# Admin Panel Guide - TEC Attendance Tracker

## 🔐 Admin-Only User Management

The TEC Attendance Tracker now features a comprehensive admin panel that provides centralized user management. **Self-registration has been disabled** - only administrators can create and manage user accounts.

## 🚀 Getting Started as Admin

### **Initial Setup**
1. **Create the first admin account:**
   ```bash
   python create_admin.py
   ```
   - Default credentials: `admin` / `admin123`
   - **IMPORTANT**: Change this password immediately after first login!

2. **Access the application:**
   - Navigate to `http://127.0.0.1:5000`
   - Login with admin credentials
   - Click your username → "Admin Panel"

## 👑 Admin Panel Features

### **Dashboard Overview**
- **User Statistics**: Total users, meetings, and attendance records
- **Quick Actions**: Add users, manage meetings, export data
- **User Management Table**: Complete user overview with actions

### **User Management**
- ✅ **Create New Users**: Add users with custom roles
- ✅ **Delete Users**: Remove users (with safety checks)
- ✅ **Reset Passwords**: Securely reset user passwords
- ✅ **Toggle Admin Status**: Grant/revoke admin privileges
- ✅ **View User Activity**: See creation dates and last login times

## 🛠️ Admin Functions

### **Creating New Users**
1. Navigate to Admin Panel → "Add New User"
2. Fill in user details:
   - **Username**: 3-20 characters, must be unique
   - **Email**: Valid email address, must be unique
   - **Password**: Minimum 6 characters
   - **Admin Privileges**: Optional checkbox
3. Click "Create User"

### **Managing Existing Users**
- **Reset Password**: Click key icon → Enter new password
- **Toggle Admin**: Click shield icon → Confirm privilege change
- **Delete User**: Click trash icon → Confirm deletion

### **Safety Features**
- ✅ Cannot delete your own account
- ✅ Cannot remove your own admin privileges
- ✅ Cannot delete the last admin user
- ✅ All actions require confirmation

## 🔒 Security Features

### **Access Control**
- Only authenticated admins can access the admin panel
- Non-admin users are redirected with error message
- All admin actions are protected by login requirements

### **Password Security**
- All passwords are securely hashed using Werkzeug
- Password resets are immediate and secure
- Minimum password length enforced (6 characters)

### **User Safety**
- Prevents accidental admin lockout
- Confirms destructive actions
- Maintains at least one admin user at all times

## 📋 Admin Responsibilities

### **User Account Management**
1. **Create accounts for new team members**
2. **Assign appropriate privileges (admin vs regular user)**
3. **Reset passwords when users forget them**
4. **Remove accounts for departing team members**
5. **Monitor user activity and last login times**

### **System Maintenance**
1. **Regular data exports for backup purposes**
2. **Monitor system usage and performance**
3. **Ensure at least one backup admin account exists**
4. **Keep admin passwords secure and updated**

## 🎯 Best Practices

### **User Creation**
- ✅ Use descriptive usernames (e.g., first.last)
- ✅ Require strong passwords (8+ characters recommended)
- ✅ Only grant admin privileges when necessary
- ✅ Verify email addresses are correct

### **Account Security**
- ✅ Change default admin password immediately
- ✅ Use unique, strong passwords for admin accounts
- ✅ Regularly review user access and remove unused accounts
- ✅ Create backup admin accounts for redundancy

### **System Administration**
- ✅ Regular data backups via CSV export
- ✅ Monitor user login activity
- ✅ Document admin account credentials securely
- ✅ Train multiple team members as admins

## 🚨 Emergency Procedures

### **Lost Admin Access**
If you lose admin access:
1. **Check existing users**: Run `python create_admin.py`
2. **Promote existing user**: Script will promote first user to admin
3. **Create new admin**: If no users exist, script creates default admin

### **Forgotten Admin Password**
1. **Use another admin account** to reset the password
2. **Or run the create_admin script** to check/create admin access
3. **Database access**: Directly modify the database if necessary

### **System Recovery**
- Admin panel provides system statistics for monitoring
- Export functionality ensures data can be backed up
- Multiple admin accounts prevent single points of failure

## 📊 Admin Panel Navigation

### **Main Sections**
1. **Dashboard**: Statistics and quick actions
2. **User Management**: Complete user administration
3. **Quick Actions**: Common administrative tasks
4. **Guidelines**: Built-in help and best practices

### **User Table Columns**
- **Username**: User's login name
- **Email**: Contact information
- **Role**: Admin or regular user status
- **Created**: Account creation date
- **Last Login**: Most recent login time
- **Actions**: Management buttons (reset, toggle, delete)

## 🔮 Future Enhancements

Planned admin features:
- 📧 Email notifications for new accounts
- 📊 Advanced user activity logging
- 🔄 Bulk user operations
- 📈 System usage analytics
- 🔐 Two-factor authentication management
- 📋 User permission granularity

The admin panel provides enterprise-level user management while maintaining simplicity and security!
