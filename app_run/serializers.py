from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ('id', 'athlete', 'comment', 'created_at')


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type')

    def get_type(self, instance):
        return 'coach' if instance.is_staff else 'athlete'
