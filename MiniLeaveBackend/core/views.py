from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import User, EmployeeProfile, Application
from .serializers import UserSerializer, EmployeeSerializer, ApplicationSerializer


# ---------------------- AUTH ----------------------

@permission_classes([IsAdminUser])
@api_view(["POST"])
def add_hr(request):
    data = request.data.copy()
    data["role"] = "hr"
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"status": "success", "message": "HR added successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response({"status": "failed", "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny]) 
@api_view(["POST"])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if not email or not password:
        return Response(
            {"status": "failed", "message": "Email and password required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=email, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "status": "success",
                "message": "Login successful",
                "role": user.role,
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )
    return Response({"status": "failed", "message": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({"status": "success", "message": "Logged out successfully"},
                        status=status.HTTP_200_OK)
    except:
        return Response({"status": "failed", "message": "No active session"},
                        status=status.HTTP_400_BAD_REQUEST)


# ---------------------- EMPLOYEE ----------------------

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_employee(request):
    if request.user.role != "hr":
        return Response({"status": "failed", "message": "Only HR can add employees"},
                        status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    serializer = EmployeeSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"status": "success", "message": "Employee added successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response({"status": "failed", "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_employee(request):
    if request.user.role != "hr":
        return Response({"status": "failed", "message": "Only HR can delete employees"},
                        status=status.HTTP_403_FORBIDDEN)

    emp_id = request.data.get("employee_id")
    if not emp_id:
        return Response({"status": "failed", "message": "Employee ID required"},
                        status=status.HTTP_400_BAD_REQUEST)

    employee = get_object_or_404(Employee, id=emp_id)
    employee.delete()
    return Response({"status": "success", "message": "Employee deleted successfully"},
                    status=status.HTTP_200_OK)


# ---------------------- LEAVE ----------------------

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def apply_for_leave(request):
    if request.user.role != "employee":
        return Response({"status": "failed", "message": "Only employees can apply for leave"},
                        status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data["employee"] = request.user.id
    serializer = ApplicationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"status": "success", "message": "Leave applied successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response({"status": "failed", "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def view_all_applications(request):
    if request.user.role != "hr":
        return Response({"status": "failed", "message": "Only HR can view applications"},
                        status=status.HTTP_403_FORBIDDEN)

    applications = LeaveApplication.objects.all()
    serializer = LeaveApplicationSerializer(applications, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def approve_leave(request, application_id):
    if request.user.role != "hr":
        return Response({"status": "failed", "message": "Only HR can approve leaves"},
                        status=status.HTTP_403_FORBIDDEN)

    application = get_object_or_404(LeaveApplication, id=application_id)
    if application.status != "pending":
        return Response({"status": "failed", "message": "Leave already processed"},
                        status=status.HTTP_400_BAD_REQUEST)

    application.status = "approved"
    application.save()
    return Response({"status": "success", "message": "Leave approved"}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reject_leave(request):
    if request.user.role != "hr":
        return Response({"status": "failed", "message": "Only HR can reject leaves"},
                        status=status.HTTP_403_FORBIDDEN)

    application_id = request.data.get("application_id")
    if not application_id:
        return Response({"status": "failed", "message": "Application ID required"},
                        status=status.HTTP_400_BAD_REQUEST)

    application = get_object_or_404(LeaveApplication, id=application_id)
    if application.status != "pending":
        return Response({"status": "failed", "message": "Leave already processed"},
                        status=status.HTTP_400_BAD_REQUEST)

    application.status = "rejected"
    application.save()
    return Response({"status": "success", "message": "Leave rejected"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_leave_balance(request, employee_id):
    if request.user.role not in ["hr", "employee"]:
        return Response({"status": "failed", "message": "Unauthorized"},
                        status=status.HTTP_403_FORBIDDEN)

    employee = get_object_or_404(Employee, id=employee_id)
    balance = employee.leave_balance if hasattr(employee, "leave_balance") else 0
    return Response({"status": "success", "leave_balance": balance}, status=status.HTTP_200_OK)
