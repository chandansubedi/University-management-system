from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
import csv
import datetime


from student_management_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, Attendance, AttendanceReport, LeaveReportStaff, FeedBackStaffs, StudentResult, Message


def staff_home(request):
    # Fetching All Students under Staff

    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_id_list = []
    for subject in subjects:
        course = Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)
    
    final_course = []
    # Removing Duplicate Course Id
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)
    
    students_count = Students.objects.filter(course_id__in=final_course).count()
    subject_count = subjects.count()

    # Fetch All Attendance Count
    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
    # Fetch All Approve Leave
    staff = Staffs.objects.get(admin=request.user.id)
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()

    #Fetch Attendance Data by Subjects
    subject_list = []
    attendance_list = []
    for subject in subjects:
        attendance_count1 = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance = Students.objects.filter(course_id__in=final_course)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []
    for student in students_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False, student_id=student.id).count()
        student_list.append(student.admin.first_name+" "+ student.admin.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context={
        "students_count": students_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_absent
    }
    return render(request, "staff_template/staff_home_template.html", context)



def staff_take_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/take_attendance_template.html", context)


def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "staff_template/staff_apply_leave_template.html", context)


def staff_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        # Server-side validation for past dates
        from datetime import date
        try:
            selected_date = date.fromisoformat(leave_date)
            today = date.today()
            
            if selected_date < today:
                messages.error(request, "You cannot apply for leave on a past date. Please select today or a future date.")
                return redirect('staff_apply_leave')
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format.")
            return redirect('staff_apply_leave')

        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStaff(staff_id=staff_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('staff_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('staff_apply_leave')


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    # Get all messages for this staff member in chronological order
    messages = Message.objects.filter(staff=staff_obj).order_by('created_at')
    context = {
        "messages": messages,
        "staff_obj": staff_obj
    }
    return render(request, "staff_template/staff_feedback_template.html", context)


def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_feedback')
    else:
        message_content = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin=request.user.id)

        try:
            # Create a new message from staff to admin
            new_message = Message(
                staff=staff_obj,
                message_type='staff_to_admin',
                content=message_content
            )
            new_message.save()
            messages.success(request, "Message Sent.")
            return redirect('staff_feedback')
        except:
            messages.error(request, "Failed to Send Message.")
            return redirect('staff_feedback')


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_students(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year")

    # Validate required fields
    if not subject_id or not session_year:
        return JsonResponse(json.dumps([]), content_type="application/json", safe=False)

    try:
        # Students enroll to Course, Course has Subjects
        # Getting all data from subject model based on subject_id
        try:
            subject_model = Subjects.objects.get(id=subject_id)
        except Subjects.DoesNotExist:
            return JsonResponse(json.dumps([]), content_type="application/json", safe=False)

        try:
            session_model = SessionYearModel.objects.get(id=session_year)
        except SessionYearModel.DoesNotExist:
            return JsonResponse(json.dumps([]), content_type="application/json", safe=False)

        # Filter students by course and session year
        students = Students.objects.filter(
            course_id=subject_model.course_id, 
            session_year_id=session_model
        ).select_related('admin')

        # Only Passing Student Id and Student Name Only
        list_data = []

        for student in students:
            if student.admin:  # Ensure admin exists
                data_small = {
                    "id": student.admin.id, 
                    "name": f"{student.admin.first_name} {student.admin.last_name}".strip()
                }
                list_data.append(data_small)

        return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
        
    except Exception as e:
        print(f"Error in get_students: {str(e)}")
        return JsonResponse(json.dumps([]), content_type="application/json", safe=False)




@csrf_exempt
def save_attendance_data(request):
    # Get Values from Staff Take Attendance form via AJAX (JavaScript)
    # Use getlist to access HTML Array/List Input Data
    student_ids = request.POST.get("student_ids")
    subject_id = request.POST.get("subject_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    # Validate required fields
    if not all([student_ids, subject_id, attendance_date, session_year_id]):
        return HttpResponse("Error: Missing required fields")

    try:
        # Get subject and session year models
        try:
            subject_model = Subjects.objects.get(id=subject_id)
        except Subjects.DoesNotExist:
            return HttpResponse("Error: Subject not found")
        
        try:
            session_year_model = SessionYearModel.objects.get(id=session_year_id)
        except SessionYearModel.DoesNotExist:
            return HttpResponse("Error: Session year not found")

        # Parse student data
        try:
            json_student = json.loads(student_ids)
        except json.JSONDecodeError:
            return HttpResponse("Error: Invalid student data format")

        if not json_student:
            return HttpResponse("Error: No students selected")

        # Check if attendance already exists for this date/subject/session
        existing_attendance = Attendance.objects.filter(
            subject_id=subject_model,
            attendance_date=attendance_date,
            session_year_id=session_year_model
        ).first()

        if existing_attendance:
            return HttpResponse("Error: Attendance already exists for this date")

        # First Attendance Data is Saved on Attendance Model
        attendance = Attendance(
            subject_id=subject_model, 
            attendance_date=attendance_date, 
            session_year_id=session_year_model
        )
        attendance.save()

        # Save individual student attendance reports
        for stud in json_student:
            try:
                student = Students.objects.get(admin=stud['id'])
                attendance_report = AttendanceReport(
                    student_id=student, 
                    attendance_id=attendance, 
                    status=bool(stud['status'])
                )
                attendance_report.save()
            except Students.DoesNotExist:
                # Skip this student if not found, but continue with others
                continue
            except Exception as e:
                # Log the error but continue with other students
                print(f"Error saving attendance for student {stud['id']}: {str(e)}")
                continue

        return HttpResponse("OK")
        
    except Exception as e:
        print(f"Error in save_attendance_data: {str(e)}")
        return HttpResponse(f"Error: {str(e)}")




def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/update_attendance_template.html", context)

@csrf_exempt
def get_attendance_dates(request):
    

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
def get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    
    if not attendance_date:
        return JsonResponse(json.dumps([]), content_type="application/json", safe=False)

    try:
        attendance = Attendance.objects.get(id=attendance_date)
    except Attendance.DoesNotExist:
        return JsonResponse(json.dumps([]), content_type="application/json", safe=False)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance).select_related('student_id__admin')
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        if student.student_id and student.student_id.admin:
            data_small = {
                "id": student.student_id.admin.id, 
                "name": f"{student.student_id.admin.first_name} {student.student_id.admin.last_name}".strip(), 
                "status": student.status
            }
            list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    attendance_date = request.POST.get("attendance_date")

    # Validate required fields
    if not student_ids or not attendance_date:
        return HttpResponse("Error: Missing required fields")

    try:
        # Get attendance record
        try:
            attendance = Attendance.objects.get(id=attendance_date)
        except Attendance.DoesNotExist:
            return HttpResponse("Error: Attendance record not found")

        # Parse student data
        try:
            json_student = json.loads(student_ids)
        except json.JSONDecodeError:
            return HttpResponse("Error: Invalid student data format")

        if not json_student:
            return HttpResponse("Error: No students selected")

        # Update individual student attendance reports
        for stud in json_student:
            try:
                student = Students.objects.get(admin=stud['id'])
                attendance_report = AttendanceReport.objects.get(
                    student_id=student, 
                    attendance_id=attendance
                )
                attendance_report.status = bool(stud['status'])
                attendance_report.save()
            except Students.DoesNotExist:
                # Skip this student if not found
                continue
            except AttendanceReport.DoesNotExist:
                # Skip if attendance report doesn't exist
                continue
            except Exception as e:
                # Log the error but continue with other students
                print(f"Error updating attendance for student {stud['id']}: {str(e)}")
                continue

        return HttpResponse("OK")
        
    except Exception as e:
        print(f"Error in update_attendance_data: {str(e)}")
        return HttpResponse(f"Error: {str(e)}")


def staff_view_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/staff_view_attendance_template.html", context)


def staff_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_view_attendance')
    else:
        # Getting all the Input Data
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        import datetime
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
        try:
            subject_obj = Subjects.objects.get(id=subject_id)
        except Subjects.DoesNotExist:
            messages.error(request, "Subject not found")
            return redirect('staff_view_attendance')

        # Now Accessing Attendance Data based on the Range of Date Selected and Subject Selected
        attendance = Attendance.objects.filter(
            attendance_date__range=(start_date_parse, end_date_parse), 
            subject_id=subject_obj
        ).order_by('attendance_date')

        # Getting Attendance Report based on the attendance details obtained above
        attendance_reports = AttendanceReport.objects.filter(
            attendance_id__in=attendance
        ).select_related('student_id__admin', 'attendance_id').order_by('attendance_id__attendance_date', 'student_id__admin__first_name')

        # Calculate summary statistics
        total_records = attendance_reports.count()
        present_count = attendance_reports.filter(status=True).count()
        absent_count = attendance_reports.filter(status=False).count()

        context = {
            "subject_obj": subject_obj,
            "attendance_reports": attendance_reports,
            "start_date": start_date,
            "end_date": end_date,
            "total_records": total_records,
            "present_count": present_count,
            "absent_count": absent_count
        }

        return render(request, 'staff_template/staff_attendance_data_template.html', context)


def staff_download_attendance_csv(request):
    """
    Download attendance data as CSV file
    """
    print(f"CSV Download Request - Method: {request.method}")  # Debug log
    
    if request.method != "POST":
        print("Invalid method - redirecting")  # Debug log
        messages.error(request, "Invalid Method")
        return redirect('staff_view_attendance')
    
    try:
        print("Processing CSV download request")  # Debug log
        # Get form data
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        print(f"Received data - Subject: {subject_id}, Start: {start_date}, End: {end_date}")  # Debug log
        
        # Validate required fields
        if not all([subject_id, start_date, end_date]):
            print("Missing required fields")  # Debug log
            messages.error(request, "Missing required fields for CSV download")
            return redirect('staff_view_attendance')
        
        # Parse dates
        try:
            start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format")
            return redirect('staff_view_attendance')
        
        # Get subject
        try:
            subject_obj = Subjects.objects.get(id=subject_id)
        except Subjects.DoesNotExist:
            messages.error(request, "Subject not found")
            return redirect('staff_view_attendance')
        
        # Verify staff has access to this subject
        if subject_obj.staff_id.id != request.user.id:
            messages.error(request, "You don't have permission to access this subject's attendance")
            return redirect('staff_view_attendance')
        
        # Get attendance data
        attendance = Attendance.objects.filter(
            attendance_date__range=(start_date_parse, end_date_parse), 
            subject_id=subject_obj
        ).order_by('attendance_date')
        
        if not attendance.exists():
            messages.warning(request, "No attendance data found for the selected date range")
            return redirect('staff_view_attendance')
        
        # Get attendance reports
        attendance_reports = AttendanceReport.objects.filter(
            attendance_id__in=attendance
        ).select_related('student_id__admin', 'attendance_id').order_by(
            'attendance_id__attendance_date', 
            'student_id__admin__first_name'
        )
        
        if not attendance_reports.exists():
            messages.warning(request, "No attendance reports found for the selected date range")
            return redirect('staff_view_attendance')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        # Clean subject name for filename
        clean_subject_name = "".join(c for c in subject_obj.subject_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"attendance_{clean_subject_name}_{start_date}_to_{end_date}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Get unique dates and students
        unique_dates = sorted(list(set([report.attendance_id.attendance_date for report in attendance_reports])))
        unique_students = {}
        
        # Group students and their attendance data
        for report in attendance_reports:
            if report.student_id and report.student_id.admin:
                student_key = f"{report.student_id.admin.first_name} {report.student_id.admin.last_name}"
                if student_key not in unique_students:
                    unique_students[student_key] = {
                        'id': report.student_id.admin.username,
                        'attendance': {}
                    }
                unique_students[student_key]['attendance'][report.attendance_id.attendance_date] = report.status
        
        # Write header row with dates as columns
        header_row = ['Student Name', 'Student ID'] + [date.strftime('%Y-%m-%d') for date in unique_dates] + ['Total Present', 'Total Absent', 'Attendance %']
        writer.writerow(header_row)
        
        # Write data rows for each student
        for student_name, student_data in sorted(unique_students.items()):
            row = [student_name, student_data['id']]
            present_count = 0
            absent_count = 0
            
            # Add attendance status for each date
            for date in unique_dates:
                if date in student_data['attendance']:
                    status = student_data['attendance'][date]
                    if status:
                        row.append('P')  # Present
                        present_count += 1
                    else:
                        row.append('A')  # Absent
                        absent_count += 1
                else:
                    row.append('-')  # No data
            
            # Add summary columns
            total_days = present_count + absent_count
            attendance_percentage = (present_count / total_days * 100) if total_days > 0 else 0
            row.extend([present_count, absent_count, f"{attendance_percentage:.1f}%"])
            
            writer.writerow(row)
        
        # Add summary section
        writer.writerow([])  # Empty row
        writer.writerow(['SUMMARY'])
        writer.writerow(['Subject', subject_obj.subject_name])
        writer.writerow(['Course', subject_obj.course_id.course_name])
        writer.writerow(['Date Range', f"{start_date} to {end_date}"])
        writer.writerow(['Total Students', len(unique_students)])
        writer.writerow(['Total Days', len(unique_dates)])
        
        # Overall statistics
        total_present = sum(1 for report in attendance_reports if report.status)
        total_absent = sum(1 for report in attendance_reports if not report.status)
        total_records = total_present + total_absent
        overall_attendance_rate = (total_present / total_records * 100) if total_records > 0 else 0
        
        writer.writerow(['Total Present Records', total_present])
        writer.writerow(['Total Absent Records', total_absent])
        writer.writerow(['Overall Attendance Rate', f"{overall_attendance_rate:.1f}%"])
        
        return response
        
    except Exception as e:
        print(f"Error in staff_download_attendance_csv: {str(e)}")
        messages.error(request, f"Error generating CSV file: {str(e)}")
        return redirect('staff_view_attendance')


def staff_download_attendance_csv_get(request):
    """
    Download attendance data as CSV file via GET request (alternative method)
    """
    print(f"CSV Download GET Request")  # Debug log
    
    try:
        # Get form data from URL parameters
        subject_id = request.GET.get('subject')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        print(f"GET data - Subject: {subject_id}, Start: {start_date}, End: {end_date}")  # Debug log
        
        # Validate required fields
        if not all([subject_id, start_date, end_date]):
            print("Missing required fields in GET request")  # Debug log
            messages.error(request, "Missing required fields for CSV download")
            return redirect('staff_view_attendance')
        
        # Parse dates
        try:
            start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format in GET request")  # Debug log
            messages.error(request, "Invalid date format")
            return redirect('staff_view_attendance')
        
        # Get subject
        try:
            subject_obj = Subjects.objects.get(id=subject_id)
        except Subjects.DoesNotExist:
            print("Subject not found in GET request")  # Debug log
            messages.error(request, "Subject not found")
            return redirect('staff_view_attendance')
        
        # Verify staff has access to this subject
        if subject_obj.staff_id.id != request.user.id:
            print("Permission denied in GET request")  # Debug log
            messages.error(request, "You don't have permission to access this subject's attendance")
            return redirect('staff_view_attendance')
        
        # Get attendance data
        attendance = Attendance.objects.filter(
            attendance_date__range=(start_date_parse, end_date_parse), 
            subject_id=subject_obj
        ).order_by('attendance_date')
        
        if not attendance.exists():
            print("No attendance data found in GET request")  # Debug log
            messages.warning(request, "No attendance data found for the selected date range")
            return redirect('staff_view_attendance')
        
        # Get attendance reports
        attendance_reports = AttendanceReport.objects.filter(
            attendance_id__in=attendance
        ).select_related('student_id__admin', 'attendance_id').order_by(
            'attendance_id__attendance_date', 
            'student_id__admin__first_name'
        )
        
        if not attendance_reports.exists():
            print("No attendance reports found in GET request")  # Debug log
            messages.warning(request, "No attendance reports found for the selected date range")
            return redirect('staff_view_attendance')
        
        print("Generating CSV file via GET request")  # Debug log
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        # Clean subject name for filename
        clean_subject_name = "".join(c for c in subject_obj.subject_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"attendance_{clean_subject_name}_{start_date}_to_{end_date}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Get unique dates and students
        unique_dates = sorted(list(set([report.attendance_id.attendance_date for report in attendance_reports])))
        unique_students = {}
        
        # Group students and their attendance data
        for report in attendance_reports:
            if report.student_id and report.student_id.admin:
                student_key = f"{report.student_id.admin.first_name} {report.student_id.admin.last_name}"
                if student_key not in unique_students:
                    unique_students[student_key] = {
                        'id': report.student_id.admin.username,
                        'attendance': {}
                    }
                unique_students[student_key]['attendance'][report.attendance_id.attendance_date] = report.status
        
        # Write header row with dates as columns
        header_row = ['Student Name', 'Student ID'] + [date.strftime('%Y-%m-%d') for date in unique_dates] + ['Total Present', 'Total Absent', 'Attendance %']
        writer.writerow(header_row)
        
        # Write data rows for each student
        for student_name, student_data in sorted(unique_students.items()):
            row = [student_name, student_data['id']]
            present_count = 0
            absent_count = 0
            
            # Add attendance status for each date
            for date in unique_dates:
                if date in student_data['attendance']:
                    status = student_data['attendance'][date]
                    if status:
                        row.append('P')  # Present
                        present_count += 1
                    else:
                        row.append('A')  # Absent
                        absent_count += 1
                else:
                    row.append('-')  # No data
            
            # Add summary columns
            total_days = present_count + absent_count
            attendance_percentage = (present_count / total_days * 100) if total_days > 0 else 0
            row.extend([present_count, absent_count, f"{attendance_percentage:.1f}%"])
            
            writer.writerow(row)
        
        # Add summary section
        writer.writerow([])  # Empty row
        writer.writerow(['SUMMARY'])
        writer.writerow(['Subject', subject_obj.subject_name])
        writer.writerow(['Course', subject_obj.course_id.course_name])
        writer.writerow(['Date Range', f"{start_date} to {end_date}"])
        writer.writerow(['Total Students', len(unique_students)])
        writer.writerow(['Total Days', len(unique_dates)])
        
        # Overall statistics
        total_present = sum(1 for report in attendance_reports if report.status)
        total_absent = sum(1 for report in attendance_reports if not report.status)
        total_records = total_present + total_absent
        overall_attendance_rate = (total_present / total_records * 100) if total_records > 0 else 0
        
        writer.writerow(['Total Present Records', total_present])
        writer.writerow(['Total Absent Records', total_absent])
        writer.writerow(['Overall Attendance Rate', f"{overall_attendance_rate:.1f}%"])
        
        print("CSV file generated successfully via GET request")  # Debug log
        return response
        
    except Exception as e:
        print(f"Error in staff_download_attendance_csv_get: {str(e)}")  # Debug log
        messages.error(request, f"Error generating CSV file: {str(e)}")
        return redirect('staff_view_attendance')


def staff_download_attendance_monthly(request):
    """
    Download attendance data for a specific month
    """
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_view_attendance')
    
    try:
        # Get form data
        subject_id = request.POST.get('subject')
        month = request.POST.get('month')
        year = request.POST.get('year')
        
        # Validate required fields
        if not all([subject_id, month, year]):
            messages.error(request, "Missing required fields for monthly CSV download")
            return redirect('staff_view_attendance')
        
        # Calculate start and end dates for the month
        start_date = datetime.date(int(year), int(month), 1)
        if int(month) == 12:
            end_date = datetime.date(int(year) + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(int(year), int(month) + 1, 1) - datetime.timedelta(days=1)
        
        # Get subject
        try:
            subject_obj = Subjects.objects.get(id=subject_id)
        except Subjects.DoesNotExist:
            messages.error(request, "Subject not found")
            return redirect('staff_view_attendance')
        
        # Verify staff has access to this subject
        if subject_obj.staff_id.id != request.user.id:
            messages.error(request, "You don't have permission to access this subject's attendance")
            return redirect('staff_view_attendance')
        
        # Get attendance data
        attendance = Attendance.objects.filter(
            attendance_date__range=(start_date, end_date), 
            subject_id=subject_obj
        ).order_by('attendance_date')
        
        if not attendance.exists():
            messages.warning(request, f"No attendance data found for {subject_obj.subject_name} in {month}/{year}")
            return redirect('staff_view_attendance')
        
        # Get attendance reports
        attendance_reports = AttendanceReport.objects.filter(
            attendance_id__in=attendance
        ).select_related('student_id__admin', 'attendance_id').order_by(
            'attendance_id__attendance_date', 
            'student_id__admin__first_name'
        )
        
        if not attendance_reports.exists():
            messages.warning(request, f"No attendance reports found for {subject_obj.subject_name} in {month}/{year}")
            return redirect('staff_view_attendance')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        # Clean subject name for filename
        clean_subject_name = "".join(c for c in subject_obj.subject_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        filename = f"attendance_{clean_subject_name}_{month_names[int(month)]}_{year}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Get unique dates and students
        unique_dates = sorted(list(set([report.attendance_id.attendance_date for report in attendance_reports])))
        unique_students = {}
        
        # Group students and their attendance data
        for report in attendance_reports:
            if report.student_id and report.student_id.admin:
                student_key = f"{report.student_id.admin.first_name} {report.student_id.admin.last_name}"
                if student_key not in unique_students:
                    unique_students[student_key] = {
                        'id': report.student_id.admin.username,
                        'attendance': {}
                    }
                unique_students[student_key]['attendance'][report.attendance_id.attendance_date] = report.status
        
        # Write header row with dates as columns
        header_row = ['Student Name', 'Student ID'] + [date.strftime('%Y-%m-%d') for date in unique_dates] + ['Total Present', 'Total Absent', 'Attendance %']
        writer.writerow(header_row)
        
        # Write data rows for each student
        for student_name, student_data in sorted(unique_students.items()):
            row = [student_name, student_data['id']]
            present_count = 0
            absent_count = 0
            
            # Add attendance status for each date
            for date in unique_dates:
                if date in student_data['attendance']:
                    status = student_data['attendance'][date]
                    if status:
                        row.append('P')  # Present
                        present_count += 1
                    else:
                        row.append('A')  # Absent
                        absent_count += 1
                else:
                    row.append('-')  # No data
            
            # Add summary columns
            total_days = present_count + absent_count
            attendance_percentage = (present_count / total_days * 100) if total_days > 0 else 0
            row.extend([present_count, absent_count, f"{attendance_percentage:.1f}%"])
            
            writer.writerow(row)
        
        # Add summary section
        writer.writerow([])  # Empty row
        writer.writerow(['SUMMARY'])
        writer.writerow(['Subject', subject_obj.subject_name])
        writer.writerow(['Course', subject_obj.course_id.course_name])
        writer.writerow(['Month', f"{month_names[int(month)]} {year}"])
        writer.writerow(['Total Students', len(unique_students)])
        writer.writerow(['Total Days', len(unique_dates)])
        
        # Overall statistics
        total_present = sum(1 for report in attendance_reports if report.status)
        total_absent = sum(1 for report in attendance_reports if not report.status)
        total_records = total_present + total_absent
        overall_attendance_rate = (total_present / total_records * 100) if total_records > 0 else 0
        
        writer.writerow(['Total Present Records', total_present])
        writer.writerow(['Total Absent Records', total_absent])
        writer.writerow(['Overall Attendance Rate', f"{overall_attendance_rate:.1f}%"])
        
        return response
        
    except Exception as e:
        print(f"Error in staff_download_attendance_monthly: {str(e)}")
        messages.error(request, f"Error generating monthly CSV file: {str(e)}")
        return redirect('staff_view_attendance')


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)
    courses = Courses.objects.all()

    context={
        "user": user,
        "staff": staff,
        "courses": courses
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')
        course_id = request.POST.get('course')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            if course_id:
                course_obj = Courses.objects.get(id=course_id)
                staff.course_id = course_obj
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')



def staff_add_result(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years,
    }
    return render(request, "staff_template/add_result_template.html", context)


def staff_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_result')
    else:
        student_admin_id = request.POST.get('student_list')
        assignment_marks = request.POST.get('assignment_marks')
        exam_marks = request.POST.get('exam_marks')
        subject_id = request.POST.get('subject')

        student_obj = Students.objects.get(admin=student_admin_id)
        subject_obj = Subjects.objects.get(id=subject_id)

        try:
            # Check if Students Result Already Exists or not
            check_exist = StudentResult.objects.filter(subject_id=subject_obj, student_id=student_obj).exists()
            if check_exist:
                result = StudentResult.objects.get(subject_id=subject_obj, student_id=student_obj)
                result.subject_assignment_marks = assignment_marks
                result.subject_exam_marks = exam_marks
                result.save()
                messages.success(request, "Result Updated Successfully!")
                return redirect('staff_add_result')
            else:
                result = StudentResult(student_id=student_obj, subject_id=subject_obj, subject_exam_marks=exam_marks, subject_assignment_marks=assignment_marks)
                result.save()
                messages.success(request, "Result Added Successfully!")
                return redirect('staff_add_result')
        except:
            messages.error(request, "Failed to Add Result!")
            return redirect('staff_add_result')
