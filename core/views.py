from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Assignment, Task, Submission, TestCase, User
# Removed server-side executor import

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'TEACHER':
                user.is_approved = False
            user.save()
            
            if user.is_approved:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.info(request, "Your teacher account has been created and is waiting for admin approval.")
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    from django.utils import timezone
    now = timezone.now()
    if request.user.role == 'TEACHER' and not request.user.is_approved:
        return render(request, 'core/waiting_approval.html')
    
    if request.user.is_teacher():
        assignments = Assignment.objects.filter(teacher=request.user)
        return render(request, 'core/teacher_dashboard.html', {'assignments': assignments, 'now': now})
    else:
        assignments = Assignment.objects.all()
        return render(request, 'core/student_dashboard.html', {'assignments': assignments, 'now': now})

@login_required
def admin_teacher_requests(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    pending_teachers = User.objects.filter(role='TEACHER', is_approved=False)
    return render(request, 'core/admin_teacher_requests.html', {'pending_teachers': pending_teachers})

@login_required
def approve_teacher(request, user_id, action):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id, role='TEACHER')
    if action == 'approve':
        user.is_approved = True
        user.save()
        messages.success(request, f"Teacher {user.username} approved.")
    elif action == 'refuse':
        user.delete()
        messages.warning(request, f"Teacher {user.username} request refused and account deleted.")
    
    return redirect('admin_teacher_requests')

# Teacher Views
@login_required
def create_assignment(request):
    if not request.user.is_teacher(): return redirect('dashboard')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time') or None
        end_time = request.POST.get('end_time') or None
        Assignment.objects.create(
            teacher=request.user, 
            title=title, 
            description=description,
            start_time=start_time,
            end_time=end_time
        )
        return redirect('dashboard')
    return render(request, 'core/create_assignment.html')

@login_required
def leaderboard(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    tasks = assignment.tasks.all()
    
    # Get all students who have submitted something for this assignment
    submissions = Submission.objects.filter(task__assignment=assignment).select_related('student', 'task')
    
    students_data = {}
    for sub in submissions:
        student = sub.student
        if student.id not in students_data:
            students_data[student.id] = {
                'username': student.username,
                'solved_count': 0,
                'task_results': {t.id: 'PENDING' for t in tasks}
            }
        
        # Keep track of the best result for each task for this student
        current_status = students_data[student.id]['task_results'].get(sub.task.id, 'PENDING')
        if sub.auto_result == 'PASS':
            if current_status != 'PASS':
                students_data[student.id]['solved_count'] += 1
            students_data[student.id]['task_results'][sub.task.id] = 'PASS'
        elif sub.auto_result == 'FAIL' and current_status != 'PASS':
            students_data[student.id]['task_results'][sub.task.id] = 'FAIL'

    # Sort students by solved_count (desc)
    sorted_students = sorted(students_data.values(), key=lambda x: x['solved_count'], reverse=True)

    context = {
        'assignment': assignment,
        'tasks': tasks,
        'students': sorted_students,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/leaderboard_table.html', context)
    return render(request, 'core/leaderboard.html', context)

@login_required
def manage_tasks(request, assignment_id):
    if not request.user.is_teacher(): return redirect('dashboard')
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher=request.user)
    tasks = assignment.tasks.all()
    return render(request, 'core/manage_tasks.html', {'assignment': assignment, 'tasks': tasks})

@login_required
def create_task(request, assignment_id):
    if not request.user.is_teacher(): return redirect('dashboard')
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        task_type = request.POST.get('task_type')
        validation_type = request.POST.get('validation_type')
        Task.objects.create(
            assignment=assignment, 
            title=title, 
            description=description, 
            task_type=task_type, 
            validation_type=validation_type
        )
        return redirect('manage_tasks', assignment_id=assignment.id)
    return render(request, 'core/create_task.html', {'assignment': assignment})

@login_required
def add_test_case(request, task_id):
    if not request.user.is_teacher(): return redirect('dashboard')
    task = get_object_or_404(Task, id=task_id, assignment__teacher=request.user)
    if request.method == 'POST':
        input_data = request.POST.get('input_data')
        expected_output = request.POST.get('expected_output')
        TestCase.objects.create(task=task, input_data=input_data, expected_output=expected_output)
        if request.headers.get('HX-Request'):
             test_cases = task.test_cases.all()
             return render(request, 'core/partials/test_case_list.html', {'test_cases': test_cases})
        return redirect('manage_tasks', assignment_id=task.assignment.id)
    return render(request, 'core/add_test_case.html', {'task': task})

# Student Views
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.is_live():
         messages.error(request, "This assignment is not currently available.")
         return redirect('dashboard')
    tasks = assignment.tasks.all()
    
    # Prepare test cases for the frontend
    tasks_data = []
    for task in tasks:
        tc_list = []
        if task.task_type == 'CODING' and task.validation_type == 'AUTO':
            for tc in task.test_cases.all():
                tc_list.append({
                    'input': tc.input_data,
                    'output': tc.expected_output.strip()
                })
        tasks_data.append({
            'id': task.id,
            'test_cases': tc_list
        })
    
    return render(request, 'core/assignment_detail.html', {
        'assignment': assignment, 
        'tasks': tasks,
        'tasks_json': json.dumps(tasks_data, cls=DjangoJSONEncoder)
    })

@login_required
def submit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        auto_result = request.POST.get('auto_result', 'PENDING')
        auto_output = request.POST.get('auto_output', '')
        
        submission = Submission.objects.create(
            student=request.user, 
            task=task, 
            content=content,
            auto_result=auto_result,
            auto_output=auto_output
        )
        
        if request.headers.get('HX-Request'):
            return render(request, 'core/partials/submission_result.html', {'submission': submission})
        
        return redirect('assignment_detail', assignment_id=task.assignment.id)
    return redirect('assignment_detail', assignment_id=task.assignment.id)

@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not request.user.is_teacher() and not assignment.teacher == request.user:
        return redirect('dashboard')
    
    submissions = Submission.objects.filter(task__assignment=assignment).order_by('-submitted_at')
    return render(request, 'core/view_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required
def grade_submission(request, submission_id):
    if not request.user.is_teacher(): return redirect('dashboard')
    submission = get_object_or_404(Submission, id=submission_id, task__assignment__teacher=request.user)
    if request.method == 'POST':
        grade = request.POST.get('grade')
        comments = request.POST.get('comments')
        submission.manual_grade = grade
        submission.teacher_comments = comments
        submission.save()
        messages.success(request, f"Graded {submission.student.username}'s submission.")
        return redirect('view_submissions', assignment_id=submission.task.assignment.id)
    return render(request, 'core/grade_submission.html', {'submission': submission})
