from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from student_management_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport, Message
from .forms import AddStudentForm, EditStudentForm


def admin_home(request):
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.admin.first_name)


    context={
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, "hod_template/add_staff_template.html", context)


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        course_id = request.POST.get('course')

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            if course_id:
                course_obj = Courses.objects.get(id=course_id)
                user.staffs.course_id = course_obj
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')



def manage_staff(request):
    courses = Courses.objects.all()
    staffs = Staffs.objects.all()
    
    # Group staff by course
    course_staff_data = {}
    for course in courses:
        course_staff = Staffs.objects.filter(course_id=course)
        course_staff_data[course] = course_staff
    
    # Staff without course assignment
    unassigned_staff = Staffs.objects.filter(course_id__isnull=True)
    
    context = {
        "courses": courses,
        "staffs": staffs,
        "course_staff_data": course_staff_data,
        "unassigned_staff": unassigned_staff
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    courses = Courses.objects.all()

    context = {
        "staff": staff,
        "id": staff_id,
        "courses": courses
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        course_id = request.POST.get('course')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate password if provided
        if new_password and new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/edit_staff/'+staff_id)

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            
            # Handle password reset
            if new_password:
                user.set_password(new_password)
                messages.success(request, "Staff Updated Successfully. Password has been reset.")
            else:
                messages.success(request, "Staff Updated Successfully.")
            
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            if course_id:
                course_obj = Courses.objects.get(id=course_id)
                staff_model.course_id = course_obj
            staff_model.save()

            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def staff_detail(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    subjects = Subjects.objects.filter(staff_id=staff.admin.id)
    
    # Get attendance data for subjects taught by this staff
    attendance_count = 0
    if subjects:
        attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
    
    # Get leave data
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
    
    context = {
        "staff": staff,
        "subjects": subjects,
        "attendance_count": attendance_count,
        "leave_count": leave_count
    }
    return render(request, "hod_template/staff_detail_template.html", context)


def course_staff_list(request, course_id):
    course = Courses.objects.get(id=course_id)
    staffs = Staffs.objects.filter(course_id=course)
    subjects = Subjects.objects.filter(course_id=course)
    
    context = {
        "course": course,
        "staffs": staffs,
        "subjects": subjects
    }
    return render(request, "hod_template/course_staff_list_template.html", context)


def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')





def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Course!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Session Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Session Year Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)




def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None


            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                user.students.address = address

                course_obj = Courses.objects.get(id=course_id)
                user.students.course_id = course_obj

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id = session_year_obj

                user.students.gender = gender
                user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            except:
                messages.error(request, "Failed to Add Student!")
                return redirect('add_student')
        else:
            return redirect('add_student')


def manage_student(request):
    courses = Courses.objects.all()
    students = Students.objects.all()
    
    # Group students by course
    course_student_data = {}
    total_assigned = 0
    for course in courses:
        course_students = Students.objects.filter(course_id=course)
        course_student_data[course] = course_students
        total_assigned += course_students.count()
    
    # Students without course assignment
    unassigned_students = Students.objects.filter(course_id__isnull=True)
    
    context = {
        "courses": courses,
        "students": students,
        "course_student_data": course_student_data,
        "unassigned_students": unassigned_students,
        "total_assigned": total_assigned
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['course_id'].initial = student.course_id.id
    form.fields['gender'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id.id

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']
            
            # Get password reset data
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Validate password if provided
            if new_password and new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('/edit_student/'+student_id)

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                
                # Handle password reset
                if new_password:
                    user.set_password(new_password)
                
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                course = Courses.objects.get(id=course_id)
                student_model.course_id = course

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                if new_password:
                    messages.success(request, "Student Updated Successfully! Password has been reset.")
                else:
                    messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_student/'+student_id)
            except:
                messages.error(request, "Failed to Update Student.")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def course_student_list(request, course_id):
    course = Courses.objects.get(id=course_id)
    students = Students.objects.filter(course_id=course)
    session_years = SessionYearModel.objects.all()
    
    context = {
        "course": course,
        "students": students,
        "session_years": session_years
    }
    return render(request, "hod_template/course_student_list_template.html", context)


def student_detail(request, student_id):
    student = Students.objects.get(admin=student_id)
    
    # Get attendance data for this student
    attendance_count = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
    
    # Get leave data
    leave_count = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
    
    # Get feedback count
    feedback_count = FeedBackStudent.objects.filter(student_id=student.id).count()
    
    context = {
        "student": student,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "feedback_count": feedback_count
    }
    return render(request, "hod_template/student_detail_template.html", context)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')

        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)
        
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name, course_id=course, staff_id=staff)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('add_subject')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject')


def manage_subject(request):
    courses = Courses.objects.all()
    subjects = Subjects.objects.all()
    
    # Group subjects by course
    course_subject_data = {}
    total_subjects = 0
    for course in courses:
        course_subjects = Subjects.objects.filter(course_id=course)
        course_subject_data[course] = course_subjects
        total_subjects += course_subjects.count()
    
    # Subjects without course assignment
    unassigned_subjects = Subjects.objects.filter(course_id__isnull=True)
    
    context = {
        "courses": courses,
        "subjects": subjects,
        "course_subject_data": course_subject_data,
        "unassigned_subjects": unassigned_subjects,
        "total_subjects": total_subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            
            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def course_subject_list(request, course_id):
    course = Courses.objects.get(id=course_id)
    subjects = Subjects.objects.filter(course_id=course)
    staffs = CustomUser.objects.filter(user_type='2')
    
    context = {
        "course": course,
        "subjects": subjects,
        "staffs": staffs
    }
    return render(request, "hod_template/course_subject_list_template.html", context)


def subject_detail(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    
    # Get attendance data for this subject
    attendance_count = Attendance.objects.filter(subject_id=subject.id).count()
    
    # Get student count enrolled in this subject's course
    student_count = Students.objects.filter(course_id=subject.course_id).count()
    
    # Get staff teaching this subject
    staff = subject.staff_id
    
    context = {
        "subject": subject,
        "attendance_count": attendance_count,
        "student_count": student_count,
        "staff": staff
    }
    return render(request, "hod_template/subject_detail_template.html", context)


def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    # Get all students who have sent messages
    students_with_messages = CustomUser.objects.filter(
        user_type=3,  # Student users
        students__messages__isnull=False
    ).distinct().order_by('first_name', 'last_name')
    
    # Group messages by student
    student_conversations = {}
    for student in students_with_messages:
        student_obj = Students.objects.get(admin=student)
        messages = Message.objects.filter(student=student_obj).order_by('created_at')
        if messages.exists():
            student_conversations[student] = list(messages)
    
    context = {
        "student_conversations": student_conversations
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    student_id = request.POST.get('id')
    message_content = request.POST.get('reply')

    try:
        # Get the student object
        student = CustomUser.objects.get(id=student_id, user_type=3)
        student_obj = Students.objects.get(admin=student)
        
        # Create a new message from admin to student
        new_message = Message(
            student=student_obj,
            message_type='admin_to_student',
            content=message_content
        )
        new_message.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    # Get all staff who have sent messages
    staff_with_messages = CustomUser.objects.filter(
        user_type=2,  # Staff users
        staffs__messages__isnull=False
    ).distinct().order_by('first_name', 'last_name')
    
    # Get all students who have sent messages
    students_with_messages = CustomUser.objects.filter(
        user_type=3,  # Student users
        students__messages__isnull=False
    ).distinct().order_by('first_name', 'last_name')
    
    # Group messages by staff member
    staff_conversations = {}
    for staff in staff_with_messages:
        staff_obj = Staffs.objects.get(admin=staff)
        messages = Message.objects.filter(staff=staff_obj).order_by('created_at')
        if messages.exists():
            staff_conversations[staff] = {
                'messages': list(messages),
                'type': 'staff'
            }
    
    # Group messages by student
    student_conversations = {}
    for student in students_with_messages:
        student_obj = Students.objects.get(admin=student)
        messages = Message.objects.filter(student=student_obj).order_by('created_at')
        if messages.exists():
            student_conversations[student] = {
                'messages': list(messages),
                'type': 'student'
            }
    
    # Combine all conversations
    all_conversations = {**staff_conversations, **student_conversations}
    
    context = {
        "all_conversations": all_conversations,
        "staff_conversations": staff_conversations,
        "student_conversations": student_conversations
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    user_id = request.POST.get('id')
    message_content = request.POST.get('reply')
    user_type = request.POST.get('user_type', 'staff')  # Default to staff for backward compatibility

    try:
        if user_type == 'student':
            # Handle student reply
            student = CustomUser.objects.get(id=user_id, user_type=3)
            student_obj = Students.objects.get(admin=student)
            
            # Create a new message from admin to student
            new_message = Message(
                student=student_obj,
                message_type='admin_to_student',
                content=message_content
            )
            new_message.save()
        else:
            # Handle staff reply (default)
            staff = CustomUser.objects.get(id=user_id, user_type=2)
            staff_obj = Staffs.objects.get(admin=staff)
            
            # Create a new message from admin to staff
            new_message = Message(
                staff=staff_obj,
                message_type='admin_to_staff',
                content=message_content
            )
            new_message.save()
        
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all().order_by('-created_at')
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all().order_by('-created_at')
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    


def staff_profile(request):
    pass


def student_profile(requtest):
    pass



