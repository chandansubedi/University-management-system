from django import forms
from .models import SubjectFile, StudentNote, FileCategory
from student_management_app.models import Subjects, SessionYearModel


class SubjectFileForm(forms.ModelForm):
    """Form for uploading subject files"""
    
    class Meta:
        model = SubjectFile
        fields = ['title', 'description', 'file', 'file_type', 'subject', 'session', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter file title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter file description (optional)'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.gif,.mp4,.avi,.mp3,.wav,.zip,.rar'
            }),
            'file_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'session': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        
        # Add help text
        self.fields['file'].help_text = "Supported formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, JPG, PNG, MP4, MP3, ZIP, RAR (Max 10MB)"
        self.fields['is_public'].help_text = "Allow all students in this subject to access this file"
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
                                '.txt', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', 
                                '.mp3', '.wav', '.zip', '.rar']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(f"File type .{file_extension} is not allowed.")
        
        return file


class StudentNoteForm(forms.ModelForm):
    """Form for creating student notes"""
    
    class Meta:
        model = StudentNote
        fields = ['title', 'content', 'subject', 'session', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter note title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter your notes here...'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'session': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_public'].help_text = "Allow other students to see this note"
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content and len(content.strip()) < 10:
            raise forms.ValidationError("Note content must be at least 10 characters long.")
        return content


class FileCategoryForm(forms.ModelForm):
    """Form for creating file categories"""
    
    class Meta:
        model = FileCategory
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description (optional)'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
