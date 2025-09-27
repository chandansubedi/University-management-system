from django.core.management.base import BaseCommand
from student_management_app.models import Courses, SessionYearModel, CustomUser, Students
from datetime import date

class Command(BaseCommand):
    help = 'Fix database by creating required default data and cleaning up'

    def handle(self, *args, **options):
        self.stdout.write("=== FIXING DATABASE ===")
        
        # 1. Create default course if none exist
        if Courses.objects.count() == 0:
            course = Courses.objects.create(course_name="Computer Science")
            self.stdout.write(self.style.SUCCESS(f"Created default course: {course.course_name} (ID: {course.id})"))
        else:
            self.stdout.write(f"Found {Courses.objects.count()} existing courses")
        
        # 2. Create default session year if none exist
        if SessionYearModel.objects.count() == 0:
            session_year = SessionYearModel.objects.create(
                session_start_year=date(2024, 1, 1),
                session_end_year=date(2024, 12, 31)
            )
            self.stdout.write(self.style.SUCCESS(f"Created default session year: {session_year.session_start_year} to {session_year.session_end_year} (ID: {session_year.id})"))
        else:
            self.stdout.write(f"Found {SessionYearModel.objects.count()} existing session years")
        
        # 3. Fix orphaned students (students without proper course/session)
        orphaned_students = Students.objects.filter(
            course_id__isnull=True
        ) | Students.objects.filter(
            session_year_id__isnull=True
        )
        
        if orphaned_students.exists():
            self.stdout.write(f"Found {orphaned_students.count()} orphaned students, fixing...")
            default_course = Courses.objects.first()
            default_session = SessionYearModel.objects.first()
            
            for student in orphaned_students:
                if not student.course_id:
                    student.course_id = default_course
                if not student.session_year_id:
                    student.session_year_id = default_session
                student.save()
            
            self.stdout.write(self.style.SUCCESS("Fixed orphaned students"))
        
        # 4. Check for users without student records
        users_without_students = CustomUser.objects.filter(user_type='3').exclude(
            id__in=Students.objects.values_list('admin_id', flat=True)
        )
        
        if users_without_students.exists():
            self.stdout.write(f"Found {users_without_students.count()} users without student records, creating...")
            default_course = Courses.objects.first()
            default_session = SessionYearModel.objects.first()
            
            for user in users_without_students:
                Students.objects.create(
                    admin=user,
                    course_id=default_course,
                    session_year_id=default_session,
                    address="",
                    profile_pic="",
                    gender=""
                )
            
            self.stdout.write(self.style.SUCCESS("Created missing student records"))
        
        self.stdout.write(self.style.SUCCESS("Database fix completed!"))
        
        # 5. Show final status
        self.stdout.write("\n=== FINAL STATUS ===")
        self.stdout.write(f"Courses: {Courses.objects.count()}")
        self.stdout.write(f"Session Years: {SessionYearModel.objects.count()}")
        self.stdout.write(f"Students: {Students.objects.count()}")
        self.stdout.write(f"Users: {CustomUser.objects.count()}")
