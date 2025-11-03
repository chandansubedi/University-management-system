from django.contrib import admin
from .models import SubjectFile, FileCategory, StudentNote, FileAccessLog


@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'description']
    list_filter = ['name']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(SubjectFile)
class SubjectFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'session', 'uploaded_by', 'file_type', 'uploaded_at', 'download_count', 'is_active']
    list_filter = ['file_type', 'is_active', 'is_public', 'uploaded_at', 'subject', 'session']
    search_fields = ['title', 'description', 'subject__subject_name', 'uploaded_by__admin__first_name', 'uploaded_by__admin__last_name']
    readonly_fields = ['uploaded_at', 'updated_at', 'download_count', 'file_size']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'file')
        }),
        ('Classification', {
            'fields': ('file_type', 'category', 'subject', 'session')
        }),
        ('Access Control', {
            'fields': ('is_public', 'is_active')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at', 'file_size', 'download_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'session', 'created_by', 'created_at', 'is_public']
    list_filter = ['is_public', 'created_at', 'subject', 'session']
    search_fields = ['title', 'content', 'subject__subject_name', 'created_by__admin__first_name', 'created_by__admin__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(FileAccessLog)
class FileAccessLogAdmin(admin.ModelAdmin):
    list_display = ['file', 'user', 'action', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp', 'file__file_type']
    search_fields = ['file__title', 'user__username', 'ip_address']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']