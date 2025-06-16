from django.contrib.auth.models import User
from rest_framework import serializers
from app_run.models import Run

class UserSerializers(serializers.ModelSerializer):
    type = serializers.SerializerMethodField() #type - вычисляемое поле

    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name', 'type')

    # Метод для вычисления поля type

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializers(read_only=True, source='athlete')
    # client_name = serializers.CharField(source='client.company_name')
    # email = serializers.CharField(source='client.user.email')

    class Meta:
        model = Run
        fields = '__all__'

