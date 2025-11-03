-- ============================================================================
-- University Management System - Database Schema (MySQL Format)
-- ============================================================================
-- This SQL file contains all table definitions for the University Management
-- System database. It can be used to create class diagrams for documentation.
--
-- Database: MySQL/MariaDB
-- Generated from Django models:
--   - student_management_app/models.py
--   - file_management/models.py
-- ============================================================================

-- ============================================================================
-- 1. USER MANAGEMENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CustomUser Table (extends Django AbstractUser)
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_customuser (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP NULL DEFAULT NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    date_joined TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_type VARCHAR(10) NOT NULL DEFAULT '1',
    CONSTRAINT user_type_check CHECK (user_type IN ('1', '2', '3'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Custom user table that extends Django AbstractUser. Stores authentication and user type information. 1=HOD, 2=Staff, 3=Student';

-- Indexes for CustomUser
CREATE INDEX idx_customuser_username ON student_management_app_customuser(username);
CREATE INDEX idx_customuser_email ON student_management_app_customuser(email);
CREATE INDEX idx_customuser_user_type ON student_management_app_customuser(user_type);

-- ----------------------------------------------------------------------------
-- Many-to-Many relationship tables for CustomUser
-- ----------------------------------------------------------------------------
-- Note: Django automatically creates these tables for groups and permissions
-- They are referenced but not defined here as they're part of Django's auth system


-- ============================================================================
-- 2. ACADEMIC STRUCTURE TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- SessionYearModel Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_sessionyearmodel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_start_year DATE NOT NULL,
    session_end_year DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores academic session periods (start and end dates)';

-- ----------------------------------------------------------------------------
-- Courses Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores course/degree program information';

-- ----------------------------------------------------------------------------
-- Subjects Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(255) NOT NULL,
    course_id INT NOT NULL DEFAULT 1,
    staff_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_subjects_course 
        FOREIGN KEY (course_id) 
        REFERENCES student_management_app_courses(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_subjects_staff 
        FOREIGN KEY (staff_id) 
        REFERENCES student_management_app_customuser(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores subject/course information linked to courses and assigned staff';

CREATE INDEX idx_subjects_course ON student_management_app_subjects(course_id);
CREATE INDEX idx_subjects_staff ON student_management_app_subjects(staff_id);


-- ============================================================================
-- 3. ADMINISTRATOR TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- AdminHOD Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_adminhod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_adminhod_user 
        FOREIGN KEY (admin_id) 
        REFERENCES student_management_app_customuser(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Head of Department (HOD) profiles linked to CustomUser';


-- ============================================================================
-- 4. STAFF TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Staffs Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_staffs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL UNIQUE,
    address TEXT NOT NULL,
    course_id INT NULL DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_staffs_user 
        FOREIGN KEY (admin_id) 
        REFERENCES student_management_app_customuser(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_staffs_course 
        FOREIGN KEY (course_id) 
        REFERENCES student_management_app_courses(id) 
        ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staff/Teacher profiles linked to CustomUser and optionally to Courses';

CREATE INDEX idx_staffs_course ON student_management_app_staffs(course_id);


-- ============================================================================
-- 5. STUDENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Students Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL UNIQUE,
    gender VARCHAR(50) NOT NULL,
    profile_pic VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    course_id INT NULL DEFAULT NULL,
    session_year_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_students_user 
        FOREIGN KEY (admin_id) 
        REFERENCES student_management_app_customuser(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_students_course 
        FOREIGN KEY (course_id) 
        REFERENCES student_management_app_courses(id) 
        ON DELETE NO ACTION,
    CONSTRAINT fk_students_session 
        FOREIGN KEY (session_year_id) 
        REFERENCES student_management_app_sessionyearmodel(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Student profiles linked to CustomUser, Courses, and SessionYear';

CREATE INDEX idx_students_course ON student_management_app_students(course_id);
CREATE INDEX idx_students_session ON student_management_app_students(session_year_id);


-- ============================================================================
-- 6. ATTENDANCE TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Attendance Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    session_year_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_subject 
        FOREIGN KEY (subject_id) 
        REFERENCES student_management_app_subjects(id) 
        ON DELETE NO ACTION,
    CONSTRAINT fk_attendance_session 
        FOREIGN KEY (session_year_id) 
        REFERENCES student_management_app_sessionyearmodel(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Subject attendance records for specific dates';

CREATE INDEX idx_attendance_subject ON student_management_app_attendance(subject_id);
CREATE INDEX idx_attendance_session ON student_management_app_attendance(session_year_id);
CREATE INDEX idx_attendance_date ON student_management_app_attendance(attendance_date);

-- ----------------------------------------------------------------------------
-- AttendanceReport Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_attendancereport (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    attendance_id INT NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendancereport_student 
        FOREIGN KEY (student_id) 
        REFERENCES student_management_app_students(id) 
        ON DELETE NO ACTION,
    CONSTRAINT fk_attendancereport_attendance 
        FOREIGN KEY (attendance_id) 
        REFERENCES student_management_app_attendance(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Individual student attendance status for each attendance record';

CREATE INDEX idx_attendancereport_student ON student_management_app_attendancereport(student_id);
CREATE INDEX idx_attendancereport_attendance ON student_management_app_attendancereport(attendance_id);


-- ============================================================================
-- 7. LEAVE MANAGEMENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- LeaveReportStudent Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_leavereportstudent (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    leave_date VARCHAR(255) NOT NULL,
    leave_message TEXT NOT NULL,
    leave_status INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_leavereportstudent_student 
        FOREIGN KEY (student_id) 
        REFERENCES student_management_app_students(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Student leave requests. leave_status: 0=pending, 1=approved, 2=rejected';

CREATE INDEX idx_leavereportstudent_student ON student_management_app_leavereportstudent(student_id);
CREATE INDEX idx_leavereportstudent_status ON student_management_app_leavereportstudent(leave_status);

-- ----------------------------------------------------------------------------
-- LeaveReportStaff Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_leavereportstaff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    leave_date VARCHAR(255) NOT NULL,
    leave_message TEXT NOT NULL,
    leave_status INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_leavereportstaff_staff 
        FOREIGN KEY (staff_id) 
        REFERENCES student_management_app_staffs(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staff leave requests. leave_status: 0=pending, 1=approved, 2=rejected';

CREATE INDEX idx_leavereportstaff_staff ON student_management_app_leavereportstaff(staff_id);
CREATE INDEX idx_leavereportstaff_status ON student_management_app_leavereportstaff(leave_status);


-- ============================================================================
-- 8. FEEDBACK TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- FeedBackStudent Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_feedbackstudent (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    feedback TEXT NOT NULL,
    feedback_reply TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedbackstudent_student 
        FOREIGN KEY (student_id) 
        REFERENCES student_management_app_students(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Student feedback and admin responses';

CREATE INDEX idx_feedbackstudent_student ON student_management_app_feedbackstudent(student_id);

-- ----------------------------------------------------------------------------
-- FeedBackStaffs Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_feedbackstaffs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    feedback TEXT NOT NULL,
    feedback_reply TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedbackstaffs_staff 
        FOREIGN KEY (staff_id) 
        REFERENCES student_management_app_staffs(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staff feedback and admin responses';

CREATE INDEX idx_feedbackstaffs_staff ON student_management_app_feedbackstaffs(staff_id);


-- ============================================================================
-- 9. MESSAGING TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Message Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NULL DEFAULT NULL,
    student_id INT NULL DEFAULT NULL,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_message_staff 
        FOREIGN KEY (staff_id) 
        REFERENCES student_management_app_staffs(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_message_student 
        FOREIGN KEY (student_id) 
        REFERENCES student_management_app_students(id) 
        ON DELETE CASCADE,
    CONSTRAINT message_type_check 
        CHECK (message_type IN ('staff_to_admin', 'admin_to_staff', 'student_to_admin', 'admin_to_student'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Messages between staff/students and admin. Either staff_id or student_id must be set, not both';

CREATE INDEX idx_message_staff ON student_management_app_message(staff_id);
CREATE INDEX idx_message_student ON student_management_app_message(student_id);
CREATE INDEX idx_message_type ON student_management_app_message(message_type);
CREATE INDEX idx_message_created_at ON student_management_app_message(created_at);


-- ============================================================================
-- 10. NOTIFICATION TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- NotificationStudent Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_notificationstudent (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_notificationstudent_student 
        FOREIGN KEY (student_id) 
        REFERENCES student_management_app_students(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Notifications sent to students';

CREATE INDEX idx_notificationstudent_student ON student_management_app_notificationstudent(student_id);
CREATE INDEX idx_notificationstudent_created_at ON student_management_app_notificationstudent(created_at);

-- ----------------------------------------------------------------------------
-- NotificationStaffs Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_notificationstaffs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stafff_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_notificationstaffs_staff 
        FOREIGN KEY (stafff_id) 
        REFERENCES student_management_app_staffs(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Notifications sent to staff. Note: column name is stafff_id (double f)';

CREATE INDEX idx_notificationstaffs_staff ON student_management_app_notificationstaffs(stafff_id);
CREATE INDEX idx_notificationstaffs_created_at ON student_management_app_notificationstaffs(created_at);


-- ============================================================================
-- 11. RESULT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- StudentResult Table
-- ----------------------------------------------------------------------------
CREATE TABLE student_management_app_studentresult (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    subject_exam_marks DOUBLE NOT NULL DEFAULT 0,
    subject_assignment_marks DOUBLE NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_studentresult_student 
        FOREIGN KEY (student_id) 
        REFERENCES student_management_app_students(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_studentresult_subject 
        FOREIGN KEY (subject_id) 
        REFERENCES student_management_app_subjects(id) 
        ON DELETE CASCADE,
    CONSTRAINT unique_student_subject 
        UNIQUE KEY unique_student_subject (student_id, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Student results/marks for subjects (exam and assignment marks)';

CREATE INDEX idx_studentresult_student ON student_management_app_studentresult(student_id);
CREATE INDEX idx_studentresult_subject ON student_management_app_studentresult(subject_id);


-- ============================================================================
-- 12. FILE MANAGEMENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- FileCategory Table
-- ----------------------------------------------------------------------------
CREATE TABLE file_management_filecategory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL DEFAULT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#007bff'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Categories for organizing files. Color column stores hex color code for category display';

CREATE INDEX idx_filecategory_name ON file_management_filecategory(name);

-- ----------------------------------------------------------------------------
-- SubjectFile Table
-- ----------------------------------------------------------------------------
CREATE TABLE file_management_subjectfile (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL DEFAULT NULL,
    file VARCHAR(100) NOT NULL,
    file_type VARCHAR(20) NOT NULL DEFAULT 'document',
    category_id BIGINT NULL DEFAULT NULL,
    subject_id INT NOT NULL,
    session_id INT NOT NULL,
    uploaded_by_id INT NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    file_size BIGINT NULL DEFAULT NULL,
    download_count INT UNSIGNED NOT NULL DEFAULT 0,
    is_public TINYINT(1) NOT NULL DEFAULT 1,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_subjectfile_category 
        FOREIGN KEY (category_id) 
        REFERENCES file_management_filecategory(id) 
        ON DELETE SET NULL,
    CONSTRAINT fk_subjectfile_subject 
        FOREIGN KEY (subject_id) 
        REFERENCES student_management_app_subjects(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_subjectfile_session 
        FOREIGN KEY (session_id) 
        REFERENCES student_management_app_sessionyearmodel(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_subjectfile_uploaded_by 
        FOREIGN KEY (uploaded_by_id) 
        REFERENCES student_management_app_staffs(id) 
        ON DELETE CASCADE,
    CONSTRAINT file_type_check 
        CHECK (file_type IN ('document', 'image', 'video', 'audio', 'archive', 'other'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Files uploaded by teachers for specific subjects. file_type: document, image, video, audio, archive, or other';

CREATE INDEX idx_subjectfile_category ON file_management_subjectfile(category_id);
CREATE INDEX idx_subjectfile_subject ON file_management_subjectfile(subject_id);
CREATE INDEX idx_subjectfile_session ON file_management_subjectfile(session_id);
CREATE INDEX idx_subjectfile_uploaded_by ON file_management_subjectfile(uploaded_by_id);
CREATE INDEX idx_subjectfile_uploaded_at ON file_management_subjectfile(uploaded_at);
CREATE INDEX idx_subjectfile_subject_session ON file_management_subjectfile(subject_id, session_id);

-- ----------------------------------------------------------------------------
-- StudentNote Table
-- ----------------------------------------------------------------------------
CREATE TABLE file_management_studentnote (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    subject_id INT NOT NULL,
    session_id INT NOT NULL,
    created_by_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_public TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_studentnote_subject 
        FOREIGN KEY (subject_id) 
        REFERENCES student_management_app_subjects(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_studentnote_session 
        FOREIGN KEY (session_id) 
        REFERENCES student_management_app_sessionyearmodel(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_studentnote_created_by 
        FOREIGN KEY (created_by_id) 
        REFERENCES student_management_app_students(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Notes created by students for subjects';

CREATE INDEX idx_studentnote_subject ON file_management_studentnote(subject_id);
CREATE INDEX idx_studentnote_session ON file_management_studentnote(session_id);
CREATE INDEX idx_studentnote_created_by ON file_management_studentnote(created_by_id);
CREATE INDEX idx_studentnote_created_at ON file_management_studentnote(created_at);
CREATE INDEX idx_studentnote_subject_session ON file_management_studentnote(subject_id, session_id);

-- ----------------------------------------------------------------------------
-- FileAccessLog Table
-- ----------------------------------------------------------------------------
CREATE TABLE file_management_fileaccesslog (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL,
    user_id INT NOT NULL,
    action VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NULL DEFAULT NULL,
    user_agent TEXT NULL DEFAULT NULL,
    CONSTRAINT fk_fileaccesslog_file 
        FOREIGN KEY (file_id) 
        REFERENCES file_management_subjectfile(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_fileaccesslog_user 
        FOREIGN KEY (user_id) 
        REFERENCES student_management_app_customuser(id) 
        ON DELETE CASCADE,
    CONSTRAINT action_check 
        CHECK (action IN ('view', 'download', 'delete'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Logs of file access activities (view, download, delete) for analytics';

CREATE INDEX idx_fileaccesslog_file ON file_management_fileaccesslog(file_id);
CREATE INDEX idx_fileaccesslog_user ON file_management_fileaccesslog(user_id);
CREATE INDEX idx_fileaccesslog_timestamp ON file_management_fileaccesslog(timestamp);
CREATE INDEX idx_fileaccesslog_file_action ON file_management_fileaccesslog(file_id, action);


-- ============================================================================
-- SUMMARY
-- ============================================================================
-- Total Tables: 21
-- 
-- User Management: 1 table
--   - CustomUser
--
-- Academic Structure: 3 tables
--   - SessionYearModel
--   - Courses
--   - Subjects
--
-- Administrator: 1 table
--   - AdminHOD
--
-- Staff: 1 table
--   - Staffs
--
-- Student: 1 table
--   - Students
--
-- Attendance: 2 tables
--   - Attendance
--   - AttendanceReport
--
-- Leave Management: 2 tables
--   - LeaveReportStudent
--   - LeaveReportStaff
--
-- Feedback: 2 tables
--   - FeedBackStudent
--   - FeedBackStaffs
--
-- Messaging: 1 table
--   - Message
--
-- Notifications: 2 tables
--   - NotificationStudent
--   - NotificationStaffs
--
-- Results: 1 table
--   - StudentResult
--
-- File Management: 4 tables
--   - FileCategory
--   - SubjectFile
--   - StudentNote
--   - FileAccessLog
--
-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
