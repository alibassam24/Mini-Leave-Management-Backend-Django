from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.



class User(AbstractUser):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    ROLE_CHOICES=[("e","employee"),("h","hr")]
    role=models.CharField(max_length=10,choices=ROLE_CHOICES)
    #id,username,email,password,first name,last name default

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

# class Leave(models.Model):
#     pass

class Application(models.Model):
    employee=models.ForeignKey(EmployeeProfile,on_delete=models.CASCADE)
    status=models.CharField(max_length=18) #pending, accepted rejected
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    start_date=models.DateField()
    end_date=models.DateField()
    reason_description=models.CharField(max_length=300)
    is_approved=models.BooleanField(default=False)
    def __str__(self):
        return self.employee.user.username