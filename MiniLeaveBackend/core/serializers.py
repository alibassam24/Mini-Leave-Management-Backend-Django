
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from rest_framework.validators import ValidationError
class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        fields=["email","password","role"]
        read_only_fields=["created_at","updated_at"]
    
    def validate(self):
        pass

class EmployeeSerializer(ModelSerializer):
    class Meta:
        model=EmployeeProfile
        fields='__all__'
        read_only_fields=['created_at','updated_at']

    def validate(self):
        pass

class HrSerializer(ModelSerializer):
    class Meta:
        model=HrProfile
        fields='__all__'
        read_only_fields=['created_at','updated_at']
    def validate(self):
        pass   
class ApplicationSerializer(ModelSerializer):
    class Meta:
        model=Application
        fields='__all__'
        read_only_fields=['created_at','updated_at','status']
    def validate(self,request):
        start=request.data.get("start_date")
        end=request.data.get("end_date")
        if start>end:
            raise serializers.ValidationError("start date cannot be ahead of end date") 
        