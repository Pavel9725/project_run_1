from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializers


@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
               'slogan': settings.SLOGAN,
               'contacts': settings.CONTACTS
    }
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer

class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False) #Исключаем передачу суперпользователей
    serializer_class = UserSerializers
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):         #фильтрация по типу тренер/атлет. Переопределение метода get_queryset
        qs = self.queryset
        type = self.request.query_params.get('type', None) #Получение параметра из запроса get
        if type == 'coach':
            qs = qs.filter(is_staff=True)
        elif type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs