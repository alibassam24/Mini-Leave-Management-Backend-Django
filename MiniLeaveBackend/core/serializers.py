
from rest_framework.serializers import ModelSerializer
from .models import *

class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        fields=["email","password","role"]
        read_only_fields=["created_at","updated_at"]
    
    def validate(self):
        pass
