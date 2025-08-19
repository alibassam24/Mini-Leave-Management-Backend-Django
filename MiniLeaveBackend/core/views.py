from django.shortcuts import render
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAdminUser

# Create your views here.


@permission_classes([IsAdminUser])
@api_view(["POST"])
def add_hr(request):
    email = request.GET.get("email")
    password = request.GET.get("password")
    role = request.GET.get("role")

@api_view(["POST"])    
def login(request):
    pass

@api_view(["POST"])
def logout(request):
    pass

@api_view(["POST"])
def add_employee(request):
    pass

@api_view(["DELETE"])
def delete_employee(request):
    pass

@api_view(["POST"])
def apply_for_leave(request):
    pass


def approve_leave(request):
    pass

def reject_leave(request):
    pass

def get_leave_balance(request,employee_id):
    pass
