from django.contrib.auth.models import User
from rest_framework import serializers
from app_run.models import Run


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

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type')

    # Метод для вычисления поля type

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'
