from django.contrib.auth.models import User
from rest_framework import serializers
from app_run.models import Run, AthleteInfo, Challenge


# serializer to api/runs nested serializer
class UserBasicSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name')


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserBasicSerializers(read_only=True, source='athlete')

    class Meta:
        model = Run
        fields = '__all__'


# serializer to api/users
class UserSerializers(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()  # type - вычисляемое поле
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished')

    # Метод для вычисления поля type
    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        return obj.runs.filter(status='finished').count()

class AthleteInfoViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = ('user_id' ,'goals', 'weight')

class ChallengeSerializer(serializers.ModelSerializer):
    athlete = serializers.IntegerField(source='athlete.user.id', read_only=True)

    class Meta:
        model = Challenge
        fields = ('full_name', 'athlete')