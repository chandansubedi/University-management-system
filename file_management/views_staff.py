from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.core.paginator import Paginator
from django.db.models import Q
import os
import mimetypes

from .models import SubjectFile, FileAccessLog
from .forms import SubjectFileForm
from student_management_app.models import Staffs, Students, Subjects, SessionYearModel


@login_required(login_url='/')
def staff_upload_file(request):
    """Staff upload file view"""
    if request.user.user_type != '2':  # Staff
        messages.error(request, "Access denied. Only staff can upload files.")
        return redirect('staff_home')
    
    try:
        staff = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        messages.error(request, "Staff profile not found. Please contact administrator.")
        return redirect('staff_home')
    
    if request.method == 'POST':
        form = SubjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.uploaded_by = staff
            
            # Calculate file size
            if file_obj.file:
                file_obj.file_size = file_obj.file.size
            
            file_obj.save()
            
            # Log the upload
            FileAccessLog.objects.create(
                file=file_obj,
                user=request.user,
                action='upload',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f"File '{file_obj.title}' uploaded successfully!")
            return redirect('staff_view_files')
    else:
        form = SubjectFileForm()
        # Filter subjects to only show those taught by this staff
        form.fields['subject'].queryset = Subjects.objects.filter(staff_id=request.user)
    
    context = {
        'form': form,
        'staff': staff,
    }
    return render(request, 'file_management/staff_upload_file.html', context)


@login_required(login_url='/')
def staff_view_files(request):
    """Staff view their uploaded files"""
    if request.user.user_type != '2':  # Staff
        messages.error(request, "Access denied. Only staff can view this page.")
        return redirect('staff_home')
    
    try:
        staff = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        messages.error(request, "Staff profile not found. Please contact administrator.")
        return redirect('staff_home')
    
    # Get files uploaded by this staff
    files = SubjectFile.objects.filter(uploaded_by=staff).order_by('-uploaded_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        files = files.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(subject__subject_name__icontains=search_query)
        )
    
    # Filter by subject
    subject_filter = request.GET.get('subject', '')
    if subject_filter:
        files = files.filter(subject_id=subject_filter)
    
    # Filter by session
    session_filter = request.GET.get('session', '')
    if session_filter:
        files = files.filter(session_id=session_filter)
    
    # Pagination
    paginator = Paginator(files, 12)  # 12 files per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    subjects = Subjects.objects.filter(staff_id=request.user)
    sessions = SessionYearModel.objects.all()
    
    context = {
        'page_obj': page_obj,
        'files': page_obj,
        'search_query': search_query,
        'subject_filter': subject_filter,
        'session_filter': session_filter,
        'subjects': subjects,
        'sessions': sessions,
        'staff': staff,
    }
    return render(request, 'file_management/staff_view_files.html', context)


@login_required(login_url='/')
def staff_delete_file(request, file_id):
    """Staff delete their uploaded file"""
    if request.user.user_type != '2':  # Staff
        messages.error(request, "Access denied.")
        return redirect('staff_home')
    
    try:
        staff = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        messages.error(request, "Staff profile not found.")
        return redirect('staff_home')
    
    file_obj = get_object_or_404(SubjectFile, id=file_id, uploaded_by=staff)
    
    if request.method == 'POST':
        # Delete file from filesystem
        if file_obj.file and os.path.isfile(file_obj.file.path):
            os.remove(file_obj.file.path)
        
        # Log the deletion
        FileAccessLog.objects.create(
            file=file_obj,
            user=request.user,
            action='delete',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        file_obj.delete()
        messages.success(request, f"File '{file_obj.title}' deleted successfully!")
        return redirect('staff_view_files')
    
    context = {
        'file': file_obj,
    }
    return render(request, 'file_management/staff_delete_file.html', context)
