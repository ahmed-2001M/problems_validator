from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    is_approved = models.BooleanField(default=True) # Default True for students, will be False for teachers

    def is_teacher(self):
        return self.role == 'TEACHER' and self.is_approved

    def is_student(self):
        return self.role == 'STUDENT'

class Assignment(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_live(self):
        from django.utils import timezone
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True

    def __str__(self):
        return self.title

class Task(models.Model):
    TYPE_CHOICES = (
        ('DESCRIPTION_ONLY', 'Description Only'),
        ('CODING', 'Coding Task'),
    )
    VALIDATION_CHOICES = (
        ('MANUAL', 'Manual Grading'),
        ('AUTO', 'Auto Validation'),
    )
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='CODING')
    validation_type = models.CharField(max_length=10, choices=VALIDATION_CHOICES, default='MANUAL')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.assignment.title} - {self.title}"

class TestCase(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField(blank=True, help_text="Input to pass to the script via stdin")
    expected_output = models.TextField(help_text="Expected output from stdout")

    def __str__(self):
        return f"Test Case for {self.task.title}"

class Submission(models.Model):
    RESULT_CHOICES = (
        ('PENDING', 'Pending'),
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('ERROR', 'Runtime Error'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField(help_text="Student's code or text answer")
    auto_result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='PENDING')
    auto_output = models.TextField(blank=True, null=True)
    manual_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.task.title}"
