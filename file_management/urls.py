from django.urls import path
from . import views

urlpatterns = [
    # Staff URLs
    path('staff/upload/', views.staff_upload_file, name='staff_upload_file'),
    path('staff/files/', views.staff_view_files, name='staff_view_files'),
    path('staff/delete/<int:file_id>/', views.staff_delete_file, name='staff_delete_file'),
    
    # Student URLs
    path('student/files/', views.student_view_files, name='student_view_files'),
    path('student/notes/', views.student_notes, name='student_notes'),
    
    # Common URLs
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('details/<int:file_id>/', views.view_file_details, name='view_file_details'),
]
