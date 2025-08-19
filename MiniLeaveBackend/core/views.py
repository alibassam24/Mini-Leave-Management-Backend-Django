from django.shortcuts import render
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAdminUser,IsAuthenticated
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
   
   email=request.data.get("email")
   password=request.data.get("password")
   if not email or not password:
       return Response({"status":"failed","message":"email/password not found"},status=status.HTTP_200_OK)

   user=authenticate(request,username=email,password=password)
   if user:
        token, _=Token.objects.get_or_create(user=user)
        return Response({"status":"success","message":"login successful","role":user.role,"token":token.key},status=status.HTTP_200_OK,)
   else:
       return Response({"status":"failed","message":"login failed"},status=status.HTTP_401_UNAUTHORIZED)



@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    pass

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_employee(request):
    if request.user.role=='hr':
        data=request.data.copy()
        data["user"]=request.user
        serializer=EmployeeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success","message":"employee added successfully","data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"status":"failed","message":"invalid data"},status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"status":"failed","message":"only allowed to HR"},status=status.HTTP_401_UNAUTHORIZED)

@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_employee(request):

    pass

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def apply_for_leave(request):
    pass


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def approve_leave(request):
    pass

@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reject_leave(request):
    pass


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_leave_balance(request,employee_id):
    pass
