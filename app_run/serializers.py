from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem


class UserRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name')


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserRunSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = ('id', 'athlete', 'comment', 'created_at', 'athlete_data', 'status', 'distance', 'run_time_seconds')


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


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ('id', 'name', 'uid', 'latitude', 'longitude', 'picture', 'value')


class UserCollectibleItemsSerializer(UserSerializer):
    items = CollectibleItemSerializer(many=True, source='collectible_items')

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('items', )


class AthleteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = ('id', 'goals', 'weight')


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ('athlete', 'full_name')


class PositionSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')

    class Meta:
        model = Position
        fields = ('id', 'run', 'latitude', 'longitude', 'date_time')

    def validate_run(self, value):
        if value.status != 'in_progress':
            raise serializers.ValidationError('Status run must be in_progress')
        return value

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError('Latitude must be between -90 and 90!')
        return round(value, 4)

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError('Longitude must be between -180 and 180!')
        return round(value, 4)
