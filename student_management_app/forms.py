from django import forms 
from django.forms import Form
from student_management_app.models import Courses, SessionYearModel, CustomUser


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    email = forms.EmailField(
        label="Email", 
        max_length=50, 
        widget=forms.EmailInput(attrs={"class":"form-control", "placeholder":"Enter email address"}),
        help_text="Enter a valid email address"
    )
    password = forms.CharField(
        label="Password", 
        min_length=6,
        max_length=50, 
        widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Enter password"}),
        help_text="Password must be at least 6 characters long"
    )
    first_name = forms.CharField(
        label="First Name", 
        max_length=50, 
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Enter first name"}),
        help_text="Enter student's first name"
    )
    last_name = forms.CharField(
        label="Last Name", 
        max_length=50, 
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Enter last name"}),
        help_text="Enter student's last name"
    )
    username = forms.CharField(
        label="Username", 
        max_length=50, 
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Enter username"}),
        help_text="Choose a unique username"
    )
    address = forms.CharField(
        label="Address", 
        max_length=200, 
        widget=forms.Textarea(attrs={"class":"form-control", "placeholder":"Enter address", "rows":3}),
        help_text="Enter student's address"
    )

    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    course_id = forms.ChoiceField(label="Course", choices=[], widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=[], widget=forms.Select(attrs={"class":"form-control"}))
    
    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        
        #For Displaying Courses - Dynamic
        try:
            courses = Courses.objects.all()
            course_list = []
            for course in courses:
                single_course = (course.id, course.course_name)
                course_list.append(single_course)
        except Exception as e:
            course_list = []
            print(f"Error loading courses: {e}")
        
        #For Displaying Session Years - Dynamic
        try:
            session_years = SessionYearModel.objects.all()
            session_year_list = []
            for session_year in session_years:
                single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
                session_year_list.append(single_session_year)
        except Exception as e:
            session_year_list = []
            print(f"Error loading session years: {e}")
        
        # If no courses exist, add a default option
        if not course_list:
            course_list = [('', 'No courses available - Please add courses first')]
        
        # If no session years exist, add a default option
        if not session_year_list:
            session_year_list = [('', 'No session years available - Please add session years first')]
        
        self.fields['course_id'].choices = course_list
        self.fields['session_year_id'].choices = session_year_list
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email
    
    # Removed course_id and session_year_id validation to prevent form errors
    # Validation is now handled in the view


class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    course_id = forms.ChoiceField(label="Course", choices=[], widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=[], widget=forms.Select(attrs={"class":"form-control"}))
    
    def __init__(self, *args, **kwargs):
        super(EditStudentForm, self).__init__(*args, **kwargs)
        
        #For Displaying Courses - Dynamic
        try:
            courses = Courses.objects.all()
            course_list = []
            for course in courses:
                single_course = (course.id, course.course_name)
                course_list.append(single_course)
        except:
            course_list = []

        #For Displaying Session Years - Dynamic
        try:
            session_years = SessionYearModel.objects.all()
            session_year_list = []
            for session_year in session_years:
                single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
                session_year_list.append(single_session_year)
        except:
            session_year_list = []
        
        self.fields['course_id'].choices = course_list
        self.fields['session_year_id'].choices = session_year_list
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))