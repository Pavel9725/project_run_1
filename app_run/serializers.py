from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run


class UserRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name')


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserRunSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = ('id', 'athlete', 'comment', 'created_at', 'athlete_data')


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type')

    def get_type(self, instance):
        return 'coach' if instance.is_staff else 'athlete'
