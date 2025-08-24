from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run, AthleteInfo, Challenge


class UserRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name')


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserRunSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = ('id', 'athlete', 'comment', 'created_at', 'athlete_data', 'status')


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(read_only=True)
    runs_finished = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished')

    def get_type(self, instance):
        return 'coach' if instance.is_staff else 'athlete'

    def get_runs_finished(self, instance):
        return instance.runs.filter(status='finished').count()

class AthleteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = ('id', 'goals', 'weight')

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ('athlete', 'full_name')
