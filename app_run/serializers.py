from django.contrib.auth.models import User
from rest_framework import serializers
from app_run.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = '__all__'

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'is_staff')