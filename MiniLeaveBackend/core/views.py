from django.shortcuts import render
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAdminUser
from .models import *
from .serializers import *
from rest_framework.authentication import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


@permission_classes([IsAdminUser])
@api_view(["POST"])
def add_hr(request):
    email = request.GET.get("email")
    password = request.GET.get("password")
    role = "hr"
    data=request.data.copy()
    data["role"]=role
    serializer=UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status":"success","message":"hr added successfully","data":serializer.data},status=status.HTTP_200_OK)
    else:
        return Response({"status":"failed","message":"invalid data",},status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])    
def login_user(request):
   try:
    email=request.data.get("email")
    password=request.data.get("password")
   except:
       return Response({"status":"failed","message":"email/password not found"},status=status.HTTP_400_BAD_REQUEST)
   user=authenticate(username=email,password=password)
   if user:
        token, +=Token.objects.get_or_create(user=user)
        return Response({"status":"success","message":"login successful","token":token},status=status.HTTP_200_OK,)
   else:
       return Response({"status":"failed","message":"login failed"},status=status.HTTP_400_BAD_REQUEST)

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
