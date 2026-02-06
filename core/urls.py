from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Teacher
    path('assignment/create/', views.create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/tasks/', views.manage_tasks, name='manage_tasks'),
    path('assignment/<int:assignment_id>/tasks/create/', views.create_task, name='create_task'),
    path('task/<int:task_id>/testcase/add/', views.add_test_case, name='add_test_case'),
    path('assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),

    # Teacher Approval Requests
    path('approvals/teachers/', views.admin_teacher_requests, name='admin_teacher_requests'),
    path('approvals/teachers/<int:user_id>/<str:action>/', views.approve_teacher, name='approve_teacher'),

    # Student
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/<int:assignment_id>/leaderboard/', views.leaderboard, name='leaderboard'),
    path('task/<int:task_id>/submit/', views.submit_task, name='submit_task'),
]
