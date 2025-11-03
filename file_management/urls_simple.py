from django.urls import path
from . import views_simple

urlpatterns = [
    path('staff/upload/', views_simple.hello_upload, name='staff_upload_file'),
    path('staff/files/', views_simple.hello_files, name='staff_view_files'),
    path('student/files/', views_simple.hello_student_files, name='student_view_files'),
]
