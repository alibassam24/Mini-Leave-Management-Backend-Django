from django.contrib.auth.models import AbstractUser
from django.db import models


# -----------------------
# Custom User Model
# -----------------------
class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ROLE_CHOICES = [
        ("employee", "Employee"),
        ("hr", "HR"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)

    # Use email as login field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # username is still required

    def __str__(self):
        return f"{self.username} ({self.role})"


# -----------------------
# Employee Profile
# -----------------------
class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employee_profile"
    )
    phone_number = models.CharField(max_length=12)
    department = models.CharField(max_length=30)
    joining_date = models.DateField()
    leave_balance = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Employee: {self.user.username}"


# -----------------------
# HR Profile
# -----------------------
class HrProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="hr_profile"
    )
    join_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"HR: {self.user.username}"


# -----------------------
# Leave Application
# -----------------------
class Application(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class LeaveType(models.TextChoices):
        SICK = "sick", "Sick Leave"
        EMERGENCY = "emergency", "Emergency Leave"
        ANNUAL = "annual", "Annual Leave"

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(
        max_length=18, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    leave_type = models.CharField(
        max_length=20, choices=LeaveType.choices, default=LeaveType.ANNUAL
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason_description = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.user.username} - {self.leave_type} ({self.status})"
