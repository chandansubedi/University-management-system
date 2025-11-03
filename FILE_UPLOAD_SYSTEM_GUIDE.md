# File Upload System - Working Guide

## ✅ **System is Now Fixed and Working!**

The file upload functionality has been fully implemented and fixed. Teachers can upload files, and students can access files based on their course and session.

---

## 📋 **How It Works**

### **For Teachers/Staff:**

1. **Upload Files**
   - Go to **Upload Files** in sidebar (only visible when logged in as staff)
   - Select **Subject** (only shows subjects taught by you)
   - Select **Session** (academic year)
   - Upload file (max 10MB)
   - Add title, description (optional)
   - Choose file type (document, image, video, etc.)
   - Set as public/private
   - Click **Upload**

2. **View Your Files**
   - Go to **My Files** in sidebar
   - See all files you uploaded
   - Filter by subject, session
   - Search files
   - View file details
   - Download or delete files

**URL**: `/files/staff/upload/` and `/files/staff/files/`

---

### **For Students:**

1. **View Subject Files**
   - Go to **Subject Files** in sidebar (only visible when logged in as student)
   - See all files for subjects in your enrolled course
   - Only see files for your current session
   - Only see files marked as "public" by teachers
   - Filter by subject, file type
   - Search files
   - View file details
   - Download files

**URL**: `/files/student/files/`

**Access Control**:
- ✅ Student can only see files where:
  1. File's subject belongs to student's course
  2. File's session matches student's session
  3. File is active and public

---

## 🔒 **Access Control Rules**

### **File Access by Course and Session:**

1. **Student Enrolled in Course A, Session 2024:**
   - ✅ Can see files for Course A subjects in Session 2024
   - ❌ Cannot see files for Course B subjects
   - ❌ Cannot see files for Session 2023 or 2025

2. **File Uploaded for Course A, Subject Math, Session 2024:**
   - ✅ Visible to all students enrolled in Course A, Session 2024
   - ❌ Not visible to students in Course B
   - ❌ Not visible to students in Session 2023

3. **File Marked as Private (`is_public=False`):**
   - ❌ Not visible to students (even if enrolled correctly)

---

## 📁 **File Organization**

### **Files are Organized By:**
- **Subject** - Which subject the file belongs to
- **Session** - Which academic year/session
- **Course** - Automatically determined by subject's course

### **File Metadata:**
- File title and description
- File type (document, image, video, audio, etc.)
- File size (displayed in human-readable format)
- Upload date and time
- Uploaded by (teacher name)
- Download count
- Category (optional)

---

## 🛠️ **What Was Fixed**

### **1. Main URLs Configuration**
- **Before**: Used `file_management.urls_simple` (placeholder views)
- **After**: Now uses `file_management.urls` (actual working views)

### **2. Access Control Logic**
- **Before**: Buggy logic checking `student.course_id.subjects_set.all()`
- **After**: Properly checks:
  - `file_obj.subject.course_id == student.course_id`
  - `file_obj.session == student.session_year_id`
  - `file_obj.is_public == True`

### **3. Student File Filtering**
- **Before**: Incorrect filtering logic
- **After**: Properly filters files by:
  - Subject's course matching student's course
  - File session matching student's session
  - File is active and public

### **4. Sidebar URLs**
- **Before**: Hardcoded URLs like `/files/staff/upload/`
- **After**: Uses Django URL names like `{% url 'staff_upload_file' %}`

---

## 📝 **File Upload Process**

### **Step-by-Step for Teachers:**

1. **Login as Staff**
2. **Navigate to Upload Files** (sidebar)
3. **Fill Upload Form:**
   - **Title**: Name of the file (required)
   - **Description**: Optional description
   - **File**: Select file to upload (max 10MB)
   - **File Type**: Document, Image, Video, Audio, etc.
   - **Subject**: Select subject (only shows your subjects)
   - **Session**: Select academic session/year
   - **Category**: Optional category
   - **Is Public**: Check if students should see it
4. **Click Upload**
5. **File is saved** and linked to:
   - Subject
   - Session
   - Your staff account

### **Supported File Types:**
- Documents: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT
- Images: JPG, JPEG, PNG, GIF
- Videos: MP4, AVI
- Audio: MP3, WAV
- Archives: ZIP, RAR

**Max File Size**: 10MB

---

## 📊 **Student File Access Process**

### **Step-by-Step for Students:**

1. **Login as Student**
2. **Navigate to Subject Files** (sidebar)
3. **See List of Files**:
   - Filtered by your course and session
   - Only public files
   - Sorted by upload date (newest first)
4. **Filter/Search**:
   - Filter by subject
   - Filter by file type
   - Search by title, description, or teacher name
5. **View File Details**:
   - Click on file to see details
   - View metadata
   - See download count
6. **Download File**:
   - Click download button
   - File downloads to your device
   - Download count increments

---

## 🔍 **File Filtering & Search**

### **For Staff:**
- Filter by **Subject** (subjects you teach)
- Filter by **Session** (academic year)
- Search by **Title**, **Description**, or **Subject Name**

### **For Students:**
- Filter by **Subject** (subjects in your course)
- Filter by **File Type** (document, image, video, etc.)
- Search by **Title**, **Description**, **Subject**, or **Teacher Name**

---

## 📂 **File Storage**

Files are stored in: `media/files/YYYY/MM/DD/`

Example: `media/files/2024/09/28/lecture_notes.pdf`

---

## ✅ **Features Implemented**

1. ✅ **Teacher File Upload** - Staff can upload files per subject and session
2. ✅ **Student File Access** - Students can view files for their enrolled course and session
3. ✅ **Access Control** - Files are filtered by course and session
4. ✅ **Public/Private Files** - Teachers can mark files as public or private
5. ✅ **File Download** - Students can download files
6. ✅ **File Management** - Teachers can view, download, and delete their files
7. ✅ **File Metadata** - File size, upload date, download count, etc.
8. ✅ **Search & Filter** - Search and filter files by various criteria
9. ✅ **Pagination** - Files are paginated (12 per page)
10. ✅ **Access Logging** - File downloads/views are logged

---

## 🎯 **How to Use**

### **As a Teacher:**

1. Login to the system
2. Go to **Upload Files** in sidebar
3. Select subject and session
4. Upload file
5. Files are automatically visible to enrolled students

### **As a Student:**

1. Login to the system
2. Go to **Subject Files** in sidebar
3. See all available files for your course and session
4. Filter and search as needed
5. Download files you need

---

## ⚙️ **Technical Details**

### **Models:**
- `SubjectFile` - Stores uploaded files with metadata
- `FileCategory` - Optional categorization
- `FileAccessLog` - Logs file access/downloads
- `StudentNote` - Students can create notes (separate feature)

### **Views:**
- `staff_upload_file` - Staff upload files
- `staff_view_files` - Staff view their files
- `staff_delete_file` - Staff delete files
- `student_view_files` - Students view available files
- `download_file` - Download file with access control
- `view_file_details` - View file details

### **URLs:**
- `/files/staff/upload/` - Upload files
- `/files/staff/files/` - View staff files
- `/files/staff/delete/<id>/` - Delete file
- `/files/student/files/` - View student files
- `/files/download/<id>/` - Download file
- `/files/details/<id>/` - View file details

---

## 🚀 **Everything is Ready!**

The file upload system is now **fully functional**:
- ✅ Teachers can upload files per subject and session
- ✅ Students can access files for their enrolled course and session
- ✅ Proper access control is in place
- ✅ All URLs are working
- ✅ Sidebar links are connected

**Start using it now!**

