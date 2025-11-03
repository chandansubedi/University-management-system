from django.db import models
from django.contrib.auth.models import User
from student_management_app.models import CustomUser, Subjects, SessionYearModel, Staffs, Students
import os
from django.utils import timezone


class FileCategory(models.Model):
    """Categories for organizing files"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    
    class Meta:
        verbose_name = "File Category"
        verbose_name_plural = "File Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SubjectFile(models.Model):
    """Files uploaded by teachers for specific subjects"""
    FILE_TYPES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('archive', 'Archive'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255, help_text="Title/Name of the file")
    description = models.TextField(blank=True, null=True, help_text="Optional description")
    file = models.FileField(upload_to='files/%Y/%m/%d/', help_text="Upload file")
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='document')
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Relationships
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, help_text="Subject this file belongs to")
    session = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE, help_text="Academic session")
    uploaded_by = models.ForeignKey(Staffs, on_delete=models.CASCADE, help_text="Teacher who uploaded this file")
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")
    download_count = models.PositiveIntegerField(default=0, help_text="Number of times downloaded")
    
    # Access control
    is_public = models.BooleanField(default=True, help_text="Can all students in the subject access this file?")
    is_active = models.BooleanField(default=True, help_text="Is this file active and visible?")
    
    class Meta:
        ordering = ['-uploaded_at']  # Newest first
        verbose_name = "Subject File"
        verbose_name_plural = "Subject Files"
        indexes = [
            models.Index(fields=['subject', 'session']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['-uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.subject.subject_name}"
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file.name)[1].lower()
    
    def get_file_size_display(self):
        """Get human readable file size"""
        if not self.file_size:
            return "Unknown"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_file_icon(self):
        """Get appropriate icon for file type"""
        ext = self.get_file_extension()
        icon_map = {
            '.pdf': 'fas fa-file-pdf text-danger',
            '.doc': 'fas fa-file-word text-primary',
            '.docx': 'fas fa-file-word text-primary',
            '.xls': 'fas fa-file-excel text-success',
            '.xlsx': 'fas fa-file-excel text-success',
            '.ppt': 'fas fa-file-powerpoint text-warning',
            '.pptx': 'fas fa-file-powerpoint text-warning',
            '.txt': 'fas fa-file-alt text-secondary',
            '.jpg': 'fas fa-file-image text-info',
            '.jpeg': 'fas fa-file-image text-info',
            '.png': 'fas fa-file-image text-info',
            '.gif': 'fas fa-file-image text-info',
            '.mp4': 'fas fa-file-video text-danger',
            '.avi': 'fas fa-file-video text-danger',
            '.mp3': 'fas fa-file-audio text-success',
            '.wav': 'fas fa-file-audio text-success',
            '.zip': 'fas fa-file-archive text-warning',
            '.rar': 'fas fa-file-archive text-warning',
        }
        return icon_map.get(ext, 'fas fa-file text-secondary')
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class StudentNote(models.Model):
    """Notes created by students"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    session = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_by = models.ForeignKey(Students, on_delete=models.CASCADE)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False, help_text="Can other students see this note?")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Student Note"
        verbose_name_plural = "Student Notes"
        indexes = [
            models.Index(fields=['subject', 'session']),
            models.Index(fields=['created_by']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.created_by.admin.first_name} {self.created_by.admin.last_name}"


class FileAccessLog(models.Model):
    """Log file access for analytics"""
    file = models.ForeignKey(SubjectFile, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=[
        ('view', 'View'),
        ('download', 'Download'),
        ('delete', 'Delete'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "File Access Log"
        verbose_name_plural = "File Access Logs"
        indexes = [
            models.Index(fields=['file', 'action']),
            models.Index(fields=['user']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.file.title}"