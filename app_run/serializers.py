from rest_framework import serializers

from app_run.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ('id', 'athlete', 'comment', 'created_at')