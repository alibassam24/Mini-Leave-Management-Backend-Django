from datetime import date

from django.db import transaction
from rest_framework import serializers

from .models import Application, EmployeeProfile, HrProfile, User


# -----------------------
# User
# -----------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "role",
            "created_at",
            "updated_at",
            "is_staff",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_staff"]

    def validate_role(self, value):
        valid = dict(User.ROLE_CHOICES).keys()
        if value not in valid:
            raise serializers.ValidationError("Invalid role.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.get("role")
        user = User(**validated_data)
        user.set_password(password)  # hash
        # If you want HRs to access Django admin / admin-only APIs, mark them as staff
        user.is_staff = role == "hr"
        user.save()
        return user


# -----------------------
# Employee
# -----------------------
class EmployeeLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ["id", "department", "joining_date", "leave_balance"]


class EmployeeSerializer(serializers.ModelSerializer):
    # Only allow users with role="employee"
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="employee")
    )

    class Meta:
        model = EmployeeProfile
        fields = [
            "id",
            "user",
            "phone_number",
            "department",
            "joining_date",
            "leave_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        user = data.get("user") or getattr(self.instance, "user", None)
        if user and user.role != "employee":
            raise serializers.ValidationError(
                {"user": "Selected user must have role 'employee'."}
            )

        # One-to-one will enforce uniqueness, but give a friendly message on create
        if (
            not self.instance
            and user
            and EmployeeProfile.objects.filter(user=user).exists()
        ):
            raise serializers.ValidationError(
                {"user": "Employee profile already exists for this user."}
            )

        phone = data.get("phone_number")
        if phone and not phone.isdigit():
            raise serializers.ValidationError(
                {"phone_number": "Phone number must contain only digits."}
            )

        if "leave_balance" in data and data["leave_balance"] < 0:
            raise serializers.ValidationError(
                {"leave_balance": "Leave balance cannot be negative."}
            )

        return data


# -----------------------
# HR
# -----------------------
class HrSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="hr"))

    class Meta:
        model = HrProfile
        fields = ["id", "user", "join_date", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        user = data.get("user") or getattr(self.instance, "user", None)
        if user and user.role != "hr":
            raise serializers.ValidationError(
                {"user": "Selected user must have role 'hr'."}
            )

        if not self.instance and user and HrProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                {"user": "HR profile already exists for this user."}
            )

        return data


# -----------------------
# Application (Leave)
# -----------------------
class ApplicationSerializer(serializers.ModelSerializer):
    # Write: supply employee id. Read: also get compact nested info.
    employee = serializers.PrimaryKeyRelatedField(
        queryset=EmployeeProfile.objects.all(), write_only=True
    )
    employee_detail = EmployeeLiteSerializer(source="employee", read_only=True)
    days = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "employee",
            "employee_detail",
            "status",
            "leave_type",
            "start_date",
            "end_date",
            "reason_description",
            "rejection_reason",
            "days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1

    # ---- Core validations (apply & edit) ----
    def _validate_dates(self, employee, start, end):
        if not start or not end:
            raise serializers.ValidationError(
                "Both start_date and end_date are required."
            )
        if start > end:
            raise serializers.ValidationError("Start date cannot be after end date.")
        if start < employee.joining_date:
            raise serializers.ValidationError(
                "Cannot apply for leave before the joining date."
            )

    def _overlap_exists(self, employee, start, end, exclude_pk=None):
        qs = Application.objects.filter(
            employee=employee,
            status__in=[
                Application.StatusChoices.PENDING,
                Application.StatusChoices.APPROVED,
            ],
            start_date__lte=end,
            end_date__gte=start,
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

    def _pending_days_other_than(self, employee, exclude_pk=None):
        qs = Application.objects.filter(
            employee=employee, status=Application.StatusChoices.PENDING
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        total = 0
        for app in qs:
            total += (app.end_date - app.start_date).days + 1
        return total

    def validate(self, data):
        # Resolve fields whether creating or updating
        instance = getattr(self, "instance", None)
        employee = data.get("employee") or (instance.employee if instance else None)
        start = data.get("start_date") or (instance.start_date if instance else None)
        end = data.get("end_date") or (instance.end_date if instance else None)
        new_status = data.get("status") or (
            instance.status if instance else Application.StatusChoices.PENDING
        )

        if not employee:
            raise serializers.ValidationError({"employee": "Employee is required."})

        # Dates & joining date
        self._validate_dates(employee, start, end)

        # Overlap with other PENDING/APPROVED applications
        if self._overlap_exists(
            employee, start, end, exclude_pk=getattr(instance, "pk", None)
        ):
            raise serializers.ValidationError(
                "Overlapping leave request exists for this employee."
            )

        # Balance check (requested + other pending must not exceed available)
        requested_days = (end - start).days + 1
        pending_others = self._pending_days_other_than(
            employee, exclude_pk=getattr(instance, "pk", None)
        )
        if requested_days + pending_others > employee.leave_balance:
            raise serializers.ValidationError(
                "Requested days exceed available leave balance when considering other pending leaves."
            )

        # Status transition rules
        if instance:
            if instance.status in [
                Application.StatusChoices.APPROVED,
                Application.StatusChoices.REJECTED,
            ]:
                # Processed apps are locked for edits except reading rejection_reason/status
                immutable_fields = {
                    "employee",
                    "start_date",
                    "end_date",
                    "leave_type",
                    "reason_description",
                }
                if any(field in data for field in immutable_fields):
                    raise serializers.ValidationError(
                        "Processed applications cannot be edited."
                    )
            # Rejecting requires a reason
            if new_status == Application.StatusChoices.REJECTED and not (
                data.get("rejection_reason") or instance.rejection_reason
            ):
                raise serializers.ValidationError(
                    {"rejection_reason": "Rejection reason is required when rejecting."}
                )

        else:
            # On create, force status to PENDING (clients shouldn't create approved/rejected)
            data["status"] = Application.StatusChoices.PENDING
            # leave_type must be present (model allows null, but API shouldn't)
            if not data.get("leave_type"):
                raise serializers.ValidationError(
                    {"leave_type": "This field is required."}
                )

        return data

    # ---- Create & Update hooks ----
    def create(self, validated_data):
        # always create as PENDING
        validated_data["status"] = Application.StatusChoices.PENDING
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        # Never allow changing the owner
        validated_data.pop("employee", None)

        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        # If moving PENDING -> APPROVED, deduct balance atomically
        if (
            old_status == Application.StatusChoices.PENDING
            and new_status == Application.StatusChoices.APPROVED
        ):
            start = validated_data.get("start_date", instance.start_date)
            end = validated_data.get("end_date", instance.end_date)
            days = (end - start).days + 1

            # Consider other pending apps, excluding this one
            pending_others = self._pending_days_other_than(
                instance.employee, exclude_pk=instance.pk
            )
            available_after_pending = instance.employee.leave_balance - pending_others
            if days > available_after_pending:
                raise serializers.ValidationError(
                    "Insufficient leave balance to approve this application."
                )

            # Deduct and save
            instance.employee.leave_balance -= days
            if instance.employee.leave_balance < 0:
                raise serializers.ValidationError("Leave balance would go negative.")
            instance.employee.save()
            # clear any old rejection reason
            validated_data.setdefault("rejection_reason", None)

        # Prevent changing away from APPROVED/REJECTED once processed
        if (
            old_status
            in [Application.StatusChoices.APPROVED, Application.StatusChoices.REJECTED]
            and new_status != old_status
        ):
            raise serializers.ValidationError(
                "Status of a processed application cannot be changed."
            )

        return super().update(instance, validated_data)
