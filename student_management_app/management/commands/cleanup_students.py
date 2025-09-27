from django.core.management.base import BaseCommand
from student_management_app.models import CustomUser, Students, Courses, SessionYearModel

class Command(BaseCommand):
    help = 'Clean up duplicate or problematic student records'

    def handle(self, *args, **options):
        self.stdout.write("=== CLEANING UP STUDENT RECORDS ===")
        
        # 1. Find duplicate student records (multiple Students records for same user)
        duplicate_students = []
        for user in CustomUser.objects.filter(user_type='3'):
            student_count = Students.objects.filter(admin=user).count()
            if student_count > 1:
                duplicate_students.append(user)
        
        if duplicate_students:
            self.stdout.write(f"Found {len(duplicate_students)} users with duplicate student records")
            for user in duplicate_students:
                # Keep the first one, delete the rest
                students = Students.objects.filter(admin=user)
                first_student = students.first()
                students.exclude(id=first_student.id).delete()
                self.stdout.write(f"  Cleaned up duplicates for user: {user.username}")
        else:
            self.stdout.write("No duplicate student records found")
        
        # 2. Find users without student records
        users_without_students = CustomUser.objects.filter(user_type='3').exclude(
            id__in=Students.objects.values_list('admin_id', flat=True)
        )
        
        if users_without_students.exists():
            self.stdout.write(f"Found {users_without_students.count()} users without student records")
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
                self.stdout.write(f"  Created student record for user: {user.username}")
        else:
            self.stdout.write("All users have student records")
        
        # 3. Find orphaned student records (Students without corresponding CustomUser)
        orphaned_students = Students.objects.exclude(
            admin__in=CustomUser.objects.filter(user_type='3')
        )
        
        if orphaned_students.exists():
            self.stdout.write(f"Found {orphaned_students.count()} orphaned student records")
            orphaned_students.delete()
            self.stdout.write("Deleted orphaned student records")
        else:
            self.stdout.write("No orphaned student records found")
        
        # 4. Show final status
        self.stdout.write("\n=== FINAL STATUS ===")
        self.stdout.write(f"Users with user_type=3: {CustomUser.objects.filter(user_type='3').count()}")
        self.stdout.write(f"Student records: {Students.objects.count()}")
        
        self.stdout.write(self.style.SUCCESS("Student cleanup completed!"))
