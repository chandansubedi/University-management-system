# HOD Admin Password Reset Process Guide

## 🔍 Overview

This document explains how HOD (Head of Department) admin accounts are created and how passwords can be reset.

---

## ❌ **NO HARDCODED PASSWORDS**

**Important**: There are **NO hardcoded passwords** in this application. All passwords must be set when creating accounts or reset through proper channels.

---

## 👤 **How HOD Admin Accounts Are Created**

### Method 1: Django Admin Panel (Superuser Creation)
1. Create a Django superuser first:
   ```bash
   python manage.py createsuperuser
   ```
   This creates a user with `is_superuser=True` and `is_staff=True`.

2. **Then** create an HOD account:
   - Login to Django admin at `/admin/`
   - Go to **CustomUser** section
   - Click **"Add CustomUser"**
   - Fill in:
     - Username
     - Email
     - Password (set via password1/password2)
     - **User Type**: Select **"1 - HOD"**
   - Click **Save**

   **Note**: When a `CustomUser` with `user_type=1` is created, a Django signal automatically creates an `AdminHOD` record (see `models.py` line 221-228).

### Method 2: Database Direct Creation
Create a `CustomUser` directly via Django shell or database:
```python
from student_management_app.models import CustomUser
user = CustomUser.objects.create_user(
    username='admin',
    email='admin@example.com',
    password='your_password',
    user_type=1  # 1 = HOD
)
```

---

## 🔐 **Password Reset Methods for HOD Admin**

### Method 1: HOD Resets Their Own Password (Self-Service)

**Location**: `/admin_profile/` (when logged in as HOD)

**Steps**:
1. HOD logs in to the application
2. Go to **Profile** → **Admin Profile** (in sidebar or dropdown menu)
3. Fill in the **Password** field (only if you want to change it)
4. Click **"Update Profile"**
5. Password is updated automatically

**Code Reference**: `HodViews.py` line 1169-1189
- View: `admin_profile_update()`
- Template: `hod_template/admin_profile.html`
- Route: `/admin_profile_update/`

**Important**: The password field is optional - leave blank to keep current password.

---

### Method 2: Django Admin Panel (Superuser Only)

**Location**: `/admin/` (requires Django superuser)

**Steps**:
1. Login as Django superuser (`is_superuser=True`)
2. Go to **CustomUsers** → Find the HOD user
3. Click on the user to edit
4. Scroll to **"New Password"** field
5. Enter new password
6. Click **Save**

**Code Reference**: `admin.py` line 22-47
- CustomUserAdmin allows password reset through Django admin

---

### Method 3: Django Management Command (Does NOT Exist)

**⚠️ Important**: There is **NO management command** to reset HOD passwords like there is for staff/students.

**Existing Commands**:
- ✅ `python manage.py reset_staff_password <username>`
- ✅ `python manage.py reset_student_password <username>`
- ❌ **NO** `reset_hod_password` command

**Workaround**: Use Django shell:
```bash
python manage.py shell
```
```python
from student_management_app.models import CustomUser
user = CustomUser.objects.get(username='hod_username', user_type=1)
user.set_password('new_password')
user.save()
```

---

### Method 4: Database Direct Reset (Emergency)

If you have database access, you can reset via SQL or Django shell:

**Django Shell**:
```python
from student_management_app.models import CustomUser
user = CustomUser.objects.get(user_type=1)  # Gets first HOD
user.set_password('new_password')
user.save()
```

**PostgreSQL/MySQL**:
```sql
-- Note: Django stores hashed passwords, not plain text
-- Use Django shell method instead for proper hashing
```

---

## 📋 **Summary Table**

| Method | Who Can Do It | Location | Requires Login? |
|--------|--------------|----------|------------------|
| **Self-Service (Profile)** | HOD themselves | `/admin_profile/` | ✅ Yes (as HOD) |
| **Django Admin Panel** | Django Superuser | `/admin/` | ✅ Yes (as superuser) |
| **Management Command** | ❌ **NOT AVAILABLE** | - | - |
| **Django Shell** | Anyone with shell access | Command line | ❌ No |
| **Database Direct** | Database admin | SQL/Shell | ❌ No |

---

## 🚨 **What If HOD Forgets Password?**

### Scenario 1: You Have Django Superuser Access
1. Login to `/admin/` as superuser
2. Find the HOD user in CustomUsers
3. Reset password using Method 2 above

### Scenario 2: You Don't Have Superuser Access
1. **Create a new superuser**:
   ```bash
   python manage.py createsuperuser
   ```
2. Then follow Scenario 1

### Scenario 3: You Have Database/Shell Access Only
Use Django shell:
```python
from student_management_app.models import CustomUser
# Find HOD user
hod = CustomUser.objects.filter(user_type=1).first()
# Reset password
hod.set_password('new_password')
hod.save()
```

---

## 🔒 **Security Notes**

1. **No Default Credentials**: The app has no default admin username/password
2. **Password Hashing**: Django automatically hashes passwords using PBKDF2
3. **User Type Checking**: HOD accounts must have `user_type=1`
4. **Signal-Based Creation**: When `user_type=1` is set, `AdminHOD` record is auto-created via signal

---

## 📝 **Code References**

- **Model**: `student_management_app/models.py`
  - CustomUser (line 17-19)
  - AdminHOD (line 23-28)
  - Signal for auto-creating AdminHOD (line 221-228)

- **Views**: `student_management_app/HodViews.py`
  - `admin_profile()` - Display profile (line 1160)
  - `admin_profile_update()` - Update password (line 1169-1189)

- **Admin Panel**: `student_management_app/admin.py`
  - CustomUserAdmin with password reset (line 22-47)

- **Management Commands**: `student_management_app/management/commands/`
  - `reset_staff_password.py` ✅
  - `reset_student_password.py` ✅
  - **NO reset_hod_password.py** ❌

---

## 💡 **Recommendation**

**Create a management command for HOD password reset** for consistency:

Create `student_management_app/management/commands/reset_hod_password.py`:
```python
from django.core.management.base import BaseCommand, CommandError
from student_management_app.models import CustomUser
import getpass

class Command(BaseCommand):
    help = 'Reset password for a HOD admin account'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username or email of the HOD')
        parser.add_argument('--password', type=str, help='New password (if not provided, will prompt for it)')

    def handle(self, *args, **options):
        username = options['username']
        new_password = options.get('password')
        
        try:
            # Try to find user by username or email
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                try:
                    user = CustomUser.objects.get(email=username)
                except CustomUser.DoesNotExist:
                    raise CommandError(f'User with username or email "{username}" does not exist.')
            
            # Check if user is HOD
            if user.user_type != 1:
                raise CommandError(f'User "{username}" is not a HOD (user_type: {user.user_type}, expected: 1)')
            
            # Get new password if not provided
            if not new_password:
                new_password = getpass.getpass('Enter new password: ')
                confirm_password = getpass.getpass('Confirm new password: ')
                if new_password != confirm_password:
                    raise CommandError('Passwords do not match.')
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully reset password for HOD "{user.username}" (email: {user.email})')
            )
            
        except Exception as e:
            raise CommandError(f'Error resetting password: {str(e)}')
```

Then use:
```bash
python manage.py reset_hod_password admin
```

