from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, FileResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
import os
import mimetypes

from .models import SubjectFile, FileCategory, StudentNote, FileAccessLog
from .forms import SubjectFileForm, StudentNoteForm
from student_management_app.models import Staffs, Students, Subjects, SessionYearModel

# Import all views from separate files
from .views_staff import staff_upload_file, staff_view_files, staff_delete_file
from .views_student import student_view_files, student_notes
from .views_common import download_file, view_file_details