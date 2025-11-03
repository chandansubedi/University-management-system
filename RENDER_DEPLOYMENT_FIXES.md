# Render Deployment Fixes Guide

This guide will help you fix all the deployment issues on Render.

## Issue 1: Add DEFAULT_AUTO_FIELD Setting

**File to edit:** `student_management_system/settings.py`

Add this setting after line 121 (after `USE_TZ = True`):

```python
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

This fixes the warning about auto-created primary key.

---

## Issue 2: Update ALLOWED_HOSTS for Render

**File to edit:** `student_management_system/settings.py`

Replace line 18:
```python
ALLOWED_HOSTS = ['.vercel.app', '127.0.0.1', '.now.sh', 'localhost']
```

With:
```python
ALLOWED_HOSTS = ['.vercel.app', '.now.sh', '127.0.0.1', 'localhost', '.onrender.com', '*']
```

Or better, use environment variable (add before ALLOWED_HOSTS):
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.vercel.app,127.0.0.1,localhost').split(',')
```

Then add `'.onrender.com'` to the list or set it via environment variable on Render.

---

## Issue 3: Update build.sh to Run Migrations

**File to edit:** `build.sh`

Replace the entire content with:
```bash
#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
```

This ensures migrations run during the build process.

---

## Issue 4: Create Start Script for Render (Port Binding)

**Create new file:** `start.sh` (in project root)

Add this content:
```bash
#!/usr/bin/env bash
set -o errexit

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Get port from Render's environment variable, default to 8000
PORT=${PORT:-8000}

# Bind to 0.0.0.0 (all interfaces) and the port from Render
exec python manage.py runserver 0.0.0.0:$PORT
```

Make it executable (you'll do this locally):
```bash
chmod +x start.sh
```

---

## Issue 5: Configure Render Service Settings

In your Render dashboard:

1. **Build Command:**
   ```
   bash build.sh
   ```

2. **Start Command:**
   ```
   bash start.sh
   ```

   OR if `start.sh` doesn't work, use:
   ```
   python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:$PORT
   ```

3. **Environment Variables:**
   - Add `ALLOWED_HOSTS` = `your-app-name.onrender.com` (replace with your actual Render domain)
   - Or use `*` (less secure, but works for testing)
   - Add `PORT` = (Render sets this automatically, but you can verify it exists)

---

## Complete Fixed settings.py Changes

Here's what your `settings.py` should look like after fixes:

### Around line 18-19:
```python
# Allow all hosts (or specify your Render domain)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',') if os.environ.get('ALLOWED_HOSTS') else ['.vercel.app', '.now.sh', '.onrender.com', '127.0.0.1', 'localhost']
```

### After line 121:
```python
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## Alternative: Use Environment Variables in settings.py

For better security, update your `settings.py` to use environment variables:

```python
import os

# ... existing code ...

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.vercel.app,.now.sh,.onrender.com,127.0.0.1,localhost').split(',')

# ... existing code ...

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## Summary of All Changes

1. ✅ Add `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` to settings.py
2. ✅ Update `ALLOWED_HOSTS` to include `.onrender.com` or use environment variable
3. ✅ Update `build.sh` to include `python manage.py migrate --noinput`
4. ✅ Create `start.sh` that binds to `$PORT` environment variable
5. ✅ Set Render start command to use `start.sh` or direct command with `$PORT`

---

## Testing Locally

Before deploying, test locally:
```bash
# Test migrations
python manage.py migrate

# Test collectstatic
python manage.py collectstatic --noinput

# Test server binding
PORT=8000 python manage.py runserver 0.0.0.0:$PORT
```

---

## After Making Changes

1. Commit all changes to git
2. Push to your repository
3. Render will automatically redeploy
4. Check the logs for any remaining issues

---

## Troubleshooting

If migrations still fail:
- Check that `student_management_app/migrations/__init__.py` exists
- Verify all migration files are committed to git
- Try running `python manage.py makemigrations` locally first

If port binding fails:
- Verify `start.sh` is executable: `chmod +x start.sh`
- Check that `$PORT` environment variable exists in Render
- Try using the direct command in Render dashboard instead of `start.sh`

