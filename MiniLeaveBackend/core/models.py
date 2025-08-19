from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.



class User(AbstractUser):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    ROLE_CHOICES=[("e","employee"),("h","hr")]
    role=models.CharField(max_length=10,choices=ROLE_CHOICES)
    email=models.EmailField(unique=True)
    #id,username,password,first name,last name default
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["username"]
    def __str__(self):
        return self.username
    

class EmployeeProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number=models.CharField(max_length=12)
    department=models.CharField(max_length=30)
    joining_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    leave_balance=models.PositiveIntegerField(default=5)
    
    def __str__(self):
        return self.user.username

class HrProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username

class Application(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING="pending","pending"
        APPROVED="approved","approved"
        REJECTED="rejected","rejected"
    class LeaveType(models.TextChoices):
        SICK="sick","sick"
        EMERGENCY="emergency","emergency"
        ANNUAL="annual","annual"
    employee=models.ForeignKey(EmployeeProfile,on_delete=models.CASCADE)
    status=models.CharField(max_length=18, default="pending") #pending, accepted rejected
    leave_type=models.CharField(choices=LeaveType,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    start_date=models.DateField()
    end_date=models.DateField()
    reason_description=models.TextField()
    rejection_reason=models.TextField(blank=True,null=True)
    
    def __str__(self):
        return self.employee.user.username