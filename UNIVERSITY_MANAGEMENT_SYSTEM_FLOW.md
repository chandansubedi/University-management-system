# University Management System - Detailed Flow Documentation

## 🎯 System Overview

A comprehensive university management system with three main user roles: **Admin (HOD)**, **Staff (Teachers)**, and **Students**. The system manages academic operations including course management, attendance tracking, student results, leave management, feedback, and messaging.

---

## 👤 Admin/HOD Journey

### 1. **Authentication & Dashboard**
- **Login** → Email/Username & Password → Role-based redirect (user_type=1)
- **Dashboard View** → View system statistics:
  - Total Students count
  - Total Staff count
  - Total Courses count
  - Total Subjects count
  - Course-wise subject and student distribution
  - Staff attendance analytics
  - Student attendance analytics (present/absent)
  - Leave statistics for staff and students

### 2. **User Management**
#### **Staff Management**
- **Add Staff** → Enter details (name, email, username, password, address, course) → Create CustomUser → Auto-create Staff record (signal)
- **Manage Staff** → View all staff → Filter by course → View staff details
- **Edit Staff** → Update profile → Modify course assignment → Save changes
- **View Staff Detail** → See staff profile → View assigned subjects → View attendance stats
- **Delete Staff** → Confirm deletion → Remove staff and user record

#### **Student Management**
- **Add Student** → Enter details (name, email, username, password, gender, address, course, session) → Create CustomUser → Auto-create Student record (signal) → Assign course & session
- **Manage Student** → View all students → Filter by course → Search students
- **Edit Student** → Update profile → Change course/session → Modify details → Save
- **View Student Detail** → See student profile → View attendance → View results → View leave history
- **Delete Student** → Confirm deletion → Remove student and user record

### 3. **Academic Structure Management**
#### **Course Management**
- **Add Course** → Enter course name → Create course record → Success confirmation
- **Manage Course** → View all courses → See course statistics (students, subjects count)
- **Edit Course** → Update course name → Save changes
- **Delete Course** → Confirm deletion → Remove course (cascade affects subjects/students)

#### **Subject Management**
- **Add Subject** → Enter subject name → Select course → Assign staff member → Create subject
- **Manage Subject** → View all subjects → Filter by course → View subject details
- **Edit Subject** → Update name/course/staff → Save changes
- **View Subject Detail** → See subject info → View enrolled students → View attendance records
- **Delete Subject** → Confirm deletion → Remove subject

#### **Session Management**
- **Add Session** → Enter start date → Enter end date → Create session year → Success
- **Manage Session** → View all sessions → See active sessions
- **Edit Session** → Update dates → Save changes
- **Delete Session** → Confirm deletion → Remove session

### 4. **Monitoring & Oversight**
#### **Attendance Monitoring**
- **View Attendance** → Select subject → Select date → View attendance records → See present/absent students
- **Get Attendance Dates** (AJAX) → Fetch dates for selected subject → Display dates
- **Get Attendance Students** (AJAX) → Fetch students for selected date → Display attendance status

#### **Leave Management**
- **View Student Leaves** → View pending leaves → Approve leave → Reject leave → View leave history
- **View Staff Leaves** → View pending leaves → Approve leave → Reject leave → View leave history
- **Leave Approval Flow**: View request → Review leave date & message → Approve (status=1) / Reject (status=2) → Notify user

#### **Feedback Management**
- **View Student Feedback** → View all student feedback → Reply to feedback → Update feedback_reply → Save
- **View Staff Feedback** → View all staff feedback → Reply to feedback → Update feedback_reply → Save
- **Feedback Reply Flow**: View feedback → Enter reply → Save response → Student/Staff sees reply

### 5. **Profile Management**
- **View Profile** → Display admin profile → Show personal info
- **Update Profile** → Modify first_name/last_name → Change password (optional) → Update email → Save changes

### 6. **Notifications** (If implemented)
- **Notify Staff** → Select staff → Enter message → Send notification → Staff receives notification
- **Notify Student** → Select student → Enter message → Send notification → Student receives notification

---

## 👨‍🏫 Staff/Teacher Journey

### 1. **Authentication & Dashboard**
- **Login** → Email/Username & Password → Role-based redirect (user_type=2)
- **Dashboard View** → View personal statistics:
  - Students under assigned subjects count
  - Total attendance taken count
  - Total leave taken count
  - Assigned subjects count
  - Subject-wise attendance statistics
  - Student-wise attendance (present/absent)

### 2. **Attendance Management**
#### **Take Attendance**
- **Select Subject** → Choose subject → Select date → Fetch enrolled students (AJAX) → Mark present/absent → Save attendance
- **Save Attendance Flow**:
  1. Create Attendance record (subject, date, session)
  2. For each student → Create AttendanceReport (status: True/False)
  3. Success confirmation

#### **View/Update Attendance**
- **View Attendance** → Select subject → Select date → View attendance records → See present/absent students
- **Update Attendance** → Select subject → Select date → Load existing records → Modify status → Update attendance
- **Download Attendance** → Export attendance data → Generate CSV → Download file
- **Monthly Attendance** → Filter by month → View monthly statistics → Download report

### 3. **Result Management**
- **Add Result** → Select student → Select subject → Enter exam marks → Enter assignment marks → Save result
- **Edit Result** → View existing results → Modify marks → Update exam/assignment scores → Save changes
- **Result Validation**: Check unique student-subject combination → Prevent duplicates

### 4. **Leave Management**
- **Apply Leave** → Enter leave date → Enter leave message → Submit request → Status: Pending (0)
- **Leave Status**: 
  - Pending (0) → Waiting for admin approval
  - Approved (1) → Admin approved leave
  - Rejected (2) → Admin rejected leave
- **View Leave History** → See all leave requests → View status → Check approval/rejection

### 5. **Feedback**
- **Submit Feedback** → Enter feedback message → Submit → Admin receives notification
- **View Feedback Reply** → Check feedback_reply field → See admin response

### 6. **Profile Management**
- **View Profile** → Display staff profile → Show assigned course → View personal info
- **Update Profile** → Modify first_name/last_name → Change password (optional) → Update email/address → Save changes

### 7. **Notifications**
- **View Notifications** → See all admin notifications → Mark as read → View message details

---

## 🎓 Student Journey

### 1. **Authentication & Dashboard**
- **Login** → Email/Username & Password → Role-based redirect (user_type=3)
- **Dashboard View** → View personal statistics:
  - Total attendance count
  - Present count
  - Absent count
  - Total subjects enrolled
  - Subject-wise attendance (present/absent breakdown)

### 2. **Attendance Tracking**
- **View Attendance** → Select subject → View attendance dates → See attendance status (present/absent)
- **Attendance Post** → Filter by date range → View filtered attendance → See attendance percentage
- **Attendance Details**: 
  - See all attendance dates for subjects
  - View present/absent status for each date
  - Calculate attendance percentage per subject

### 3. **Results Viewing**
- **View Results** → See all subjects → View exam marks → View assignment marks → See total marks
- **Result Display**: 
  - Subject name
  - Exam marks (subject_exam_marks)
  - Assignment marks (subject_assignment_marks)
  - Total/Percentage calculation

### 4. **Leave Management**
- **Apply Leave** → Enter leave date → Enter leave message → Submit request → Status: Pending (0)
- **Leave Flow**:
  - Submit leave → Admin receives notification
  - Admin approves/rejects → Student sees status update
  - Approved leave → Leave status = 1
  - Rejected leave → Leave status = 2
- **View Leave History** → See all leave requests → Check approval status

### 5. **Feedback**
- **Submit Feedback** → Enter feedback message → Submit → Admin receives notification
- **View Feedback Reply** → Check feedback_reply field → See admin response

### 6. **Profile Management**
- **View Profile** → Display student profile → Show enrolled course → View session → See personal info
- **Update Profile** → Modify first_name/last_name → Change password (optional) → Update email/address/gender → Save changes

### 7. **Notifications**
- **View Notifications** → See all admin notifications → View message details

---

## 🔄 Common Flows

### **Authentication Flow**
1. User enters login page
2. Enter email/username & password
3. System validates credentials (EmailBackEnd)
4. Check user_type:
   - user_type = 1 → Admin dashboard
   - user_type = 2 → Staff dashboard
   - user_type = 3 → Student dashboard
5. Session created → Redirect to respective home

### **User Creation Flow** (Admin creates Staff/Student)
1. Admin fills user form
2. System validates data (username uniqueness, email format)
3. Create CustomUser with appropriate user_type
4. Django signal (post_save) triggered:
   - If user_type=2 → Auto-create Staffs record
   - If user_type=3 → Auto-create Students record (with default course/session if needed)
5. Success notification → Redirect

### **Attendance Recording Flow**
1. Staff selects subject & date
2. System fetches enrolled students (AJAX get_students)
3. Staff marks present/absent for each student
4. Staff saves attendance (AJAX save_attendance_data)
5. System creates:
   - One Attendance record (subject, date, session)
   - Multiple AttendanceReport records (one per student with status)
6. Success confirmation

### **Leave Approval Flow**
1. Student/Staff submits leave request
2. System creates LeaveReport record (status=0: Pending)
3. Admin views pending leaves
4. Admin reviews request (date, message)
5. Admin approves (status=1) or rejects (status=2)
6. User can view updated status

### **Feedback Flow**
1. Student/Staff submits feedback
2. System creates FeedBack record (feedback filled, feedback_reply empty)
3. Admin views feedback
4. Admin enters reply
5. System updates feedback_reply field
6. User views feedback with admin reply

### **Result Entry Flow**
1. Staff selects student & subject
2. Staff enters exam marks & assignment marks
3. System validates (checks unique student-subject combination)
4. System creates/updates StudentResult record
5. Student can view their results

---

## 📊 Key Database Relationships

### **User Hierarchy**
- CustomUser (base user) → AdminHOD / Staffs / Students (OneToOne)
- CustomUser.user_type determines role:
  - 1 = Admin/HOD
  - 2 = Staff
  - 3 = Student

### **Academic Structure**
- Courses → Multiple Subjects (ForeignKey)
- Subjects → One Course (ForeignKey) + One Staff (ForeignKey to CustomUser)
- Students → One Course (ForeignKey) + One Session (ForeignKey)

### **Attendance Chain**
- Subjects → Multiple Attendance records (ForeignKey)
- Attendance → One Subject (ForeignKey) + One Session (ForeignKey)
- Attendance → Multiple AttendanceReport records (ForeignKey)
- AttendanceReport → One Student (ForeignKey) + One Attendance (ForeignKey)

### **Results**
- StudentResult → One Student (ForeignKey) + One Subject (ForeignKey)
- Unique constraint: (student_id, subject_id) combination

---

## 🎯 Key Takeaways

### **Admin Journey**
1. **Setup**: Login → Dashboard → View statistics
2. **User Management**: Add Staff → Add Student → Manage users → View details
3. **Academic Structure**: Create Courses → Add Subjects → Assign Staff → Create Sessions
4. **Monitoring**: View Attendance → Approve Leaves → Reply Feedback → Track analytics
5. **Oversight**: Monitor system → View reports → Manage content → Support users

### **Staff Journey**
1. **Setup**: Login → Dashboard → View assigned students/subjects
2. **Teaching**: Take Attendance → Record attendance → Update attendance
3. **Assessment**: Add Results → Enter marks → Edit results
4. **Communication**: Apply Leave → Submit Feedback → Check notifications
5. **Management**: View attendance stats → Export reports → Manage profile

### **Student Journey**
1. **Discovery**: Login → Dashboard → View statistics
2. **Learning**: View Attendance → Check attendance status → Calculate percentage
3. **Performance**: View Results → See marks → Track progress
4. **Communication**: Apply Leave → Submit Feedback → View notifications
5. **Engagement**: Track attendance → Monitor results → Manage profile

---

## 🔐 Security & Access Control

- **Middleware**: LoginCheckMiddleWare validates user authentication on every request
- **Role-based Access**: User type determines available features and URLs
- **Authentication Backend**: Custom EmailBackEnd allows login via email/username
- **Session Management**: Django sessions track logged-in users

---

## 📝 Notes for Sequence Diagrams

### **When Creating Sequence Diagrams:**

1. **Authentication Sequence**:
   - Actor: User (Admin/Staff/Student)
   - Components: Login Page → Authentication Backend → Database → Dashboard

2. **User Creation Sequence**:
   - Actor: Admin
   - Components: Admin → Create User Form → Database → Signal Handler → User Record Created

3. **Attendance Sequence**:
   - Actor: Staff
   - Components: Staff → Select Subject → Fetch Students → Mark Attendance → Save → Database

4. **Leave Approval Sequence**:
   - Actor: Student/Staff → Admin
   - Components: User → Submit Leave → Admin → Review → Approve/Reject → Database → Notification

5. **Result Entry Sequence**:
   - Actor: Staff
   - Components: Staff → Select Student/Subject → Enter Marks → Save → Database → Student View

6. **Feedback Sequence**:
   - Actor: Student/Staff → Admin
   - Components: User → Submit Feedback → Admin → Reply → Database → User View

This documentation excludes file upload functionality as requested.

