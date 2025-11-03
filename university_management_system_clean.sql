CREATE TABLE student_management_app_customuser (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    date_joined TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_type VARCHAR(10) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_customuser_username ON student_management_app_customuser(username);
CREATE INDEX idx_customuser_email ON student_management_app_customuser(email);
CREATE INDEX idx_customuser_user_type ON student_management_app_customuser(user_type);

CREATE TABLE student_management_app_sessionyearmodel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_start_year DATE NOT NULL,
    session_end_year DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE student_management_app_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE student_management_app_subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(255) NOT NULL,
    course_id INT NOT NULL DEFAULT 1,
    staff_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES student_management_app_courses(id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES student_management_app_customuser(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_subjects_course ON student_management_app_subjects(course_id);
CREATE INDEX idx_subjects_staff ON student_management_app_subjects(staff_id);

CREATE TABLE student_management_app_adminhod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES student_management_app_customuser(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE student_management_app_staffs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL UNIQUE,
    address TEXT NOT NULL,
    course_id INT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES student_management_app_customuser(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES student_management_app_courses(id) ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_staffs_course ON student_management_app_staffs(course_id);

CREATE TABLE student_management_app_students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL UNIQUE,
    gender VARCHAR(50) NOT NULL,
    profile_pic VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    course_id INT NULL,
    session_year_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES student_management_app_customuser(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES student_management_app_courses(id) ON DELETE NO ACTION,
    FOREIGN KEY (session_year_id) REFERENCES student_management_app_sessionyearmodel(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_students_course ON student_management_app_students(course_id);
CREATE INDEX idx_students_session ON student_management_app_students(session_year_id);

CREATE TABLE student_management_app_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    session_year_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES student_management_app_subjects(id) ON DELETE NO ACTION,
    FOREIGN KEY (session_year_id) REFERENCES student_management_app_sessionyearmodel(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_attendance_subject ON student_management_app_attendance(subject_id);
CREATE INDEX idx_attendance_session ON student_management_app_attendance(session_year_id);
CREATE INDEX idx_attendance_date ON student_management_app_attendance(attendance_date);

CREATE TABLE student_management_app_attendancereport (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    attendance_id INT NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_management_app_students(id) ON DELETE NO ACTION,
    FOREIGN KEY (attendance_id) REFERENCES student_management_app_attendance(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_attendancereport_student ON student_management_app_attendancereport(student_id);
CREATE INDEX idx_attendancereport_attendance ON student_management_app_attendancereport(attendance_id);

CREATE TABLE student_management_app_leavereportstudent (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    leave_date VARCHAR(255) NOT NULL,
    leave_message TEXT NOT NULL,
    leave_status INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_management_app_students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_leavereportstudent_student ON student_management_app_leavereportstudent(student_id);
CREATE INDEX idx_leavereportstudent_status ON student_management_app_leavereportstudent(leave_status);

CREATE TABLE student_management_app_leavereportstaff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    leave_date VARCHAR(255) NOT NULL,
    leave_message TEXT NOT NULL,
    leave_status INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES student_management_app_staffs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_leavereportstaff_staff ON student_management_app_leavereportstaff(staff_id);
CREATE INDEX idx_leavereportstaff_status ON student_management_app_leavereportstaff(leave_status);

CREATE TABLE student_management_app_feedbackstudent (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    feedback TEXT NOT NULL,
    feedback_reply TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_management_app_students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_feedbackstudent_student ON student_management_app_feedbackstudent(student_id);

CREATE TABLE student_management_app_feedbackstaffs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    feedback TEXT NOT NULL,
    feedback_reply TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES student_management_app_staffs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_feedbackstaffs_staff ON student_management_app_feedbackstaffs(staff_id);

CREATE TABLE student_management_app_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NULL,
    student_id INT NULL,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES student_management_app_staffs(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES student_management_app_students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_message_staff ON student_management_app_message(staff_id);
CREATE INDEX idx_message_student ON student_management_app_message(student_id);
CREATE INDEX idx_message_type ON student_management_app_message(message_type);
CREATE INDEX idx_message_created_at ON student_management_app_message(created_at);

CREATE TABLE student_management_app_notificationstudent (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_management_app_students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_notificationstudent_student ON student_management_app_notificationstudent(student_id);
CREATE INDEX idx_notificationstudent_created_at ON student_management_app_notificationstudent(created_at);

CREATE TABLE student_management_app_notificationstaffs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stafff_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (stafff_id) REFERENCES student_management_app_staffs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_notificationstaffs_staff ON student_management_app_notificationstaffs(stafff_id);
CREATE INDEX idx_notificationstaffs_created_at ON student_management_app_notificationstaffs(created_at);

CREATE TABLE student_management_app_studentresult (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    subject_exam_marks DOUBLE NOT NULL DEFAULT 0,
    subject_assignment_marks DOUBLE NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_management_app_students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES student_management_app_subjects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_subject (student_id, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_studentresult_student ON student_management_app_studentresult(student_id);
CREATE INDEX idx_studentresult_subject ON student_management_app_studentresult(subject_id);

CREATE TABLE file_management_filecategory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#007bff'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_filecategory_name ON file_management_filecategory(name);

CREATE TABLE file_management_subjectfile (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    file VARCHAR(100) NOT NULL,
    file_type VARCHAR(20) NOT NULL DEFAULT 'document',
    category_id BIGINT NULL,
    subject_id INT NOT NULL,
    session_id INT NOT NULL,
    uploaded_by_id INT NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    file_size BIGINT NULL,
    download_count INT UNSIGNED NOT NULL DEFAULT 0,
    is_public TINYINT(1) NOT NULL DEFAULT 1,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES file_management_filecategory(id) ON DELETE SET NULL,
    FOREIGN KEY (subject_id) REFERENCES student_management_app_subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES student_management_app_sessionyearmodel(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by_id) REFERENCES student_management_app_staffs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_subjectfile_category ON file_management_subjectfile(category_id);
CREATE INDEX idx_subjectfile_subject ON file_management_subjectfile(subject_id);
CREATE INDEX idx_subjectfile_session ON file_management_subjectfile(session_id);
CREATE INDEX idx_subjectfile_uploaded_by ON file_management_subjectfile(uploaded_by_id);
CREATE INDEX idx_subjectfile_uploaded_at ON file_management_subjectfile(uploaded_at);
CREATE INDEX idx_subjectfile_subject_session ON file_management_subjectfile(subject_id, session_id);

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
    FOREIGN KEY (subject_id) REFERENCES student_management_app_subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES student_management_app_sessionyearmodel(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_id) REFERENCES student_management_app_students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_studentnote_subject ON file_management_studentnote(subject_id);
CREATE INDEX idx_studentnote_session ON file_management_studentnote(session_id);
CREATE INDEX idx_studentnote_created_by ON file_management_studentnote(created_by_id);
CREATE INDEX idx_studentnote_created_at ON file_management_studentnote(created_at);
CREATE INDEX idx_studentnote_subject_session ON file_management_studentnote(subject_id, session_id);

CREATE TABLE file_management_fileaccesslog (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL,
    user_id INT NOT NULL,
    action VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    FOREIGN KEY (file_id) REFERENCES file_management_subjectfile(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES student_management_app_customuser(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_fileaccesslog_file ON file_management_fileaccesslog(file_id);
CREATE INDEX idx_fileaccesslog_user ON file_management_fileaccesslog(user_id);
CREATE INDEX idx_fileaccesslog_timestamp ON file_management_fileaccesslog(timestamp);
CREATE INDEX idx_fileaccesslog_file_action ON file_management_fileaccesslog(file_id, action);
