"""
Django management command to import assignments from JSON files.

Usage:
    python manage.py import_assignment <file_path> --teacher <username>
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from core.services.assignment_importer import AssignmentImporter, AssignmentImportError

User = get_user_model()


class Command(BaseCommand):
    help = 'Import an assignment from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the JSON file containing assignment data'
        )
        parser.add_argument(
            '--teacher',
            type=str,
            required=True,
            help='Username of the teacher who will own this assignment'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        teacher_username = options['teacher']
        verbose = options.get('verbose', False)

        # Get teacher user
        try:
            teacher = User.objects.get(username=teacher_username)
        except User.DoesNotExist:
            raise CommandError(f"User '{teacher_username}' does not exist")

        if not teacher.is_teacher():
            raise CommandError(f"User '{teacher_username}' is not a teacher")

        # Import assignment
        try:
            if verbose:
                self.stdout.write(f"Importing assignment from: {file_path}")
                self.stdout.write(f"Teacher: {teacher_username}")
            
            importer = AssignmentImporter(teacher)
            assignment = importer.import_from_file(file_path)
            
            # Success message
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully imported assignment: '{assignment.title}' (ID: {assignment.id})"
                )
            )
            
            if verbose:
                self.stdout.write(f"  - Tasks created: {assignment.tasks.count()}")
                for task in assignment.tasks.all():
                    tc_count = task.test_cases.count()
                    self.stdout.write(f"    • {task.title} ({tc_count} test cases)")
            
        except AssignmentImportError as e:
            raise CommandError(f"Import failed: {e}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {e}")
