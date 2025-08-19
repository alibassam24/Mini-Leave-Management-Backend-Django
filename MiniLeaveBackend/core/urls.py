from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout, name="logout"),

    # HR Management
    path("hr/add/", views.add_hr, name="add_hr"),

    # Employee Management
    path("employee/add/", views.add_employee, name="add_employee"),
    path("employee/delete/", views.delete_employee, name="delete_employee"),

    # Leave Applications
    path("leave/apply/", views.apply_for_leave, name="apply_leave"),
    path("leave/applications/", views.view_all_applications, name="view_all_applications"),
    path("leave/approve/<int:application_id>/", views.approve_leave, name="approve_leave"),
    path("leave/reject/<int:application_id>/", views.reject_leave, name="reject_leave"),
    path("leave/balance/<int:employee_id>/", views.get_leave_balance, name="leave_balance"),
]
