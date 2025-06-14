from django.contrib.auth.models import User
from rest_framework import serializers
from app_run.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = '__all__'

class UserSerializers(serializers.ModelSerializer):
    type = serializers.SerializerMethodField() #type - вычисляемое поле

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type')

    # Метод для вычисления поля type

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'