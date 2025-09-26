from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from django.utils.html import format_html
from .models import CustomUser, AdminHOD, Staffs, Courses, Subjects, Students, Attendance, AttendanceReport, LeaveReportStudent, LeaveReportStaff, FeedBackStudent, FeedBackStaffs, NotificationStudent, NotificationStaffs

# Custom form for changing user password in admin
class CustomUserChangeForm(UserChangeForm):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Leave blank to keep current password, or enter a new password."
    )
    
    class Meta:
        model = CustomUser
        fields = '__all__'

# Custom User Admin with password change functionality
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password', 'new_password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Handle password change
        if change and form.cleaned_data.get('new_password'):
            obj.set_password(form.cleaned_data['new_password'])
        super().save_model(request, obj, form, change)

# Custom Student Admin with password change
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admin', 'course_id', 'gender', 'address', 'created_at')
    list_filter = ('course_id', 'gender', 'created_at')
    search_fields = ('admin__username', 'admin__email', 'admin__first_name', 'admin__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Student Information', {
            'fields': ('admin', 'gender', 'profile_pic', 'address', 'course_id', 'session_year_id')
        }),
        ('Password Management', {
            'fields': ('new_password',),
            'description': 'Enter a new password for this student. Leave blank to keep current password.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def new_password(self, obj):
        return format_html(
            '<input type="password" name="new_password" class="form-control" placeholder="Enter new password">'
        )
    new_password.short_description = "New Password"
    
    def save_model(self, request, obj, form, change):
        # Handle password change for student
        new_password = request.POST.get('new_password')
        if new_password:
            obj.admin.set_password(new_password)
            obj.admin.save()
        super().save_model(request, obj, form, change)

# Custom Staff Admin with password change
class StaffAdmin(admin.ModelAdmin):
    list_display = ('admin', 'address', 'course_id', 'created_at')
    list_filter = ('course_id', 'created_at')
    search_fields = ('admin__username', 'admin__email', 'admin__first_name', 'admin__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('admin', 'address', 'course_id')
        }),
        ('Password Management', {
            'fields': ('new_password',),
            'description': 'Enter a new password for this staff member. Leave blank to keep current password.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def new_password(self, obj):
        return format_html(
            '<input type="password" name="new_password" class="form-control" placeholder="Enter new password">'
        )
    new_password.short_description = "New Password"
    
    def save_model(self, request, obj, form, change):
        # Handle password change for staff
        new_password = request.POST.get('new_password')
        if new_password:
            obj.admin.set_password(new_password)
            obj.admin.save()
        super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AdminHOD)
admin.site.register(Staffs, StaffAdmin)
admin.site.register(Courses)
admin.site.register(Subjects)
admin.site.register(Students, StudentAdmin)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(LeaveReportStudent)
admin.site.register(LeaveReportStaff)
admin.site.register(FeedBackStudent)
admin.site.register(FeedBackStaffs)
admin.site.register(NotificationStudent)
admin.site.register(NotificationStaffs)
