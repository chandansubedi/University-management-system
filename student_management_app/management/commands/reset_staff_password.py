from django.core.management.base import BaseCommand, CommandError
from student_management_app.models import CustomUser, Staffs
import getpass

class Command(BaseCommand):
    help = 'Reset password for a staff account'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username or email of the staff member')
        parser.add_argument('--password', type=str, help='New password (if not provided, will prompt for it)')

    def handle(self, *args, **options):
        username = options['username']
        new_password = options.get('password')
        
        try:
            # Try to find user by username or email
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                try:
                    user = CustomUser.objects.get(email=username)
                except CustomUser.DoesNotExist:
                    raise CommandError(f'User with username or email "{username}" does not exist.')
            
            # Check if user is a staff member
            if user.user_type != 2:
                raise CommandError(f'User "{username}" is not a staff member (user_type: {user.user_type})')
            
            # Get new password if not provided
            if not new_password:
                new_password = getpass.getpass('Enter new password: ')
                confirm_password = getpass.getpass('Confirm new password: ')
                if new_password != confirm_password:
                    raise CommandError('Passwords do not match.')
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully reset password for staff member "{user.username}" (email: {user.email})')
            )
            
        except Exception as e:
            raise CommandError(f'Error resetting password: {str(e)}')
