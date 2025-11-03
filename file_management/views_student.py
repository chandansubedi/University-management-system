from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.core.paginator import Paginator
from django.db.models import Q
import os
import mimetypes

from .models import SubjectFile, StudentNote, FileAccessLog
from .forms import StudentNoteForm
from student_management_app.models import Staffs, Students, Subjects, SessionYearModel


@login_required(login_url='/')
def student_view_files(request):
    """Student view files for their enrolled subjects"""
    if request.user.user_type != '3':  # Student
        messages.error(request, "Access denied. Only students can view this page.")
        return redirect('student_home')
    
    try:
        student = Students.objects.get(admin=request.user)
    except Students.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact administrator.")
        return redirect('student_home')
    
    # Get files for subjects the student is enrolled in
    student_subjects = student.course_id.subjects_set.all()
    files = SubjectFile.objects.filter(
        subject__in=student_subjects,
        session=student.session_year_id,
        is_active=True
    ).order_by('-uploaded_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        files = files.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(subject__subject_name__icontains=search_query) |
            Q(uploaded_by__admin__first_name__icontains=search_query) |
            Q(uploaded_by__admin__last_name__icontains=search_query)
        )
    
    # Filter by subject
    subject_filter = request.GET.get('subject', '')
    if subject_filter:
        files = files.filter(subject_id=subject_filter)
    
    # Filter by file type
    type_filter = request.GET.get('type', '')
    if type_filter:
        files = files.filter(file_type=type_filter)
    
    # Pagination
    paginator = Paginator(files, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    subjects = student_subjects
    file_types = SubjectFile.FILE_TYPES
    
    context = {
        'page_obj': page_obj,
        'files': page_obj,
        'search_query': search_query,
        'subject_filter': subject_filter,
        'type_filter': type_filter,
        'subjects': subjects,
        'file_types': file_types,
        'student': student,
    }
    return render(request, 'file_management/student_view_files.html', context)


@login_required(login_url='/')
def student_notes(request):
    """Student notes management"""
    if request.user.user_type != '3':  # Student
        messages.error(request, "Access denied. Only students can access notes.")
        return redirect('student_home')
    
    try:
        student = Students.objects.get(admin=request.user)
    except Students.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('student_home')
    
    if request.method == 'POST':
        form = StudentNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.created_by = student
            note.save()
            messages.success(request, "Note created successfully!")
            return redirect('student_notes')
    else:
        form = StudentNoteForm()
        # Filter subjects to only show those the student is enrolled in
        form.fields['subject'].queryset = student.course_id.subjects_set.all()
    
    # Get student's notes
    notes = StudentNote.objects.filter(created_by=student).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(subject__subject_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(notes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'notes': page_obj,
        'search_query': search_query,
        'student': student,
    }
    return render(request, 'file_management/student_notes.html', context)
