from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
import os
import mimetypes

from .models import SubjectFile, FileAccessLog
from student_management_app.models import Staffs, Students


@login_required(login_url='/')
def download_file(request, file_id):
    """Download file with access control"""
    file_obj = get_object_or_404(SubjectFile, id=file_id, is_active=True)
    
    # Check access permissions
    if request.user.user_type == '2':  # Staff
        try:
            staff = Staffs.objects.get(admin=request.user)
            if file_obj.uploaded_by != staff:
                messages.error(request, "Access denied. You can only download your own files.")
                return redirect('staff_view_files')
        except Staffs.DoesNotExist:
            messages.error(request, "Staff profile not found.")
            return redirect('staff_home')
    
    elif request.user.user_type == '3':  # Student
        try:
            student = Students.objects.get(admin=request.user)
            # Check if student is enrolled in the subject and session
            # Student can access if:
            # 1. File's subject belongs to student's course
            # 2. File's session matches student's session
            # 3. File is active and public
            if not student.course_id:
                messages.error(request, "Student course not assigned. Please contact administrator.")
                return redirect('student_home')
            
            if (file_obj.subject.course_id != student.course_id or 
                file_obj.session != student.session_year_id):
                messages.error(request, "Access denied. You don't have permission to download this file.")
                return redirect('student_view_files')
            
            if not file_obj.is_public:
                messages.error(request, "Access denied. This file is not available for download.")
                return redirect('student_view_files')
        except Students.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect('student_home')
    
    else:
        messages.error(request, "Access denied.")
        return redirect('login')
    
    # Check if file exists
    if not file_obj.file or not os.path.isfile(file_obj.file.path):
        messages.error(request, "File not found on server.")
        return redirect('student_view_files' if request.user.user_type == '3' else 'staff_view_files')
    
    # Increment download count
    file_obj.increment_download_count()
    
    # Log the download
    FileAccessLog.objects.create(
        file=file_obj,
        user=request.user,
        action='download',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Serve the file
    try:
        response = FileResponse(
            open(file_obj.file.path, 'rb'),
            content_type=mimetypes.guess_type(file_obj.file.path)[0] or 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{file_obj.title}{file_obj.get_file_extension()}"'
        return response
    except Exception as e:
        messages.error(request, f"Error downloading file: {str(e)}")
        return redirect('student_view_files' if request.user.user_type == '3' else 'staff_view_files')


@login_required(login_url='/')
def view_file_details(request, file_id):
    """View file details"""
    file_obj = get_object_or_404(SubjectFile, id=file_id, is_active=True)
    
    # Check access permissions (same logic as download)
    if request.user.user_type == '2':  # Staff
        try:
            staff = Staffs.objects.get(admin=request.user)
            if file_obj.uploaded_by != staff:
                messages.error(request, "Access denied.")
                return redirect('staff_view_files')
        except Staffs.DoesNotExist:
            messages.error(request, "Staff profile not found.")
            return redirect('staff_home')
    
    elif request.user.user_type == '3':  # Student
        try:
            student = Students.objects.get(admin=request.user)
            # Check if student is enrolled in the subject and session
            if not student.course_id:
                messages.error(request, "Student course not assigned. Please contact administrator.")
                return redirect('student_home')
            
            if (file_obj.subject.course_id != student.course_id or 
                file_obj.session != student.session_year_id):
                messages.error(request, "Access denied.")
                return redirect('student_view_files')
            
            if not file_obj.is_public:
                messages.error(request, "Access denied. This file is not available for viewing.")
                return redirect('student_view_files')
        except Students.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect('student_home')
    
    else:
        messages.error(request, "Access denied.")
        return redirect('login')
    
    # Log the view
    FileAccessLog.objects.create(
        file=file_obj,
        user=request.user,
        action='view',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    context = {
        'file': file_obj,
    }
    
    # Render different templates based on user type
    if request.user.user_type == '2':
        return render(request, 'file_management/staff_file_details.html', context)
    else:
        return render(request, 'file_management/student_file_details.html', context)
