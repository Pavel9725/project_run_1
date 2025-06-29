from gc import get_objects

from django.conf import settings
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from app_run.models import Run, AthleteInfo
from app_run.serializers import RunSerializer, UserSerializers, AthleteInfoViewSerializer


@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
               'slogan': settings.SLOGAN,
               'contacts': settings.CONTACTS
               }
    return Response(details)


class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'


class UserPagination(PageNumberPagination):
    page_size_query_param = 'size'


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    ordering = ['id']  # default sort
    pagination_class = RunPagination


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)  # Исключаем передачу суперпользователей
    serializer_class = UserSerializers
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = UserPagination

    def get_queryset(self):  # фильтрация по типу тренер/атлет. Переопределение метода get_queryset
        qs = self.queryset
        type = self.request.query_params.get('type', None)  # Получение параметра из запроса get
        if type == 'coach':
            qs = qs.filter(is_staff=True)
        elif type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class StartRunView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)

        if run.status != 'init':
            return Response({'detail': 'Invalid run status for starting.'}, status=status.HTTP_400_BAD_REQUEST)

        run.status = 'in_progress'
        run.save()
        return Response(RunSerializer(run).data, status=status.HTTP_200_OK)


class StopRunView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)

        if run.status != 'in_progress':
            return Response({'detail': 'Invalid run status for stopping.'}, status=status.HTTP_400_BAD_REQUEST)

        run.status = 'finished'
        run.save()
        return Response(RunSerializer(run).data, status=status.HTTP_200_OK)


# METHOD_2: @api_view(['POST'])
@api_view(['POST'])
def start_run_view(request, run_id):
    run = get_object_or_404(Run, id=run_id)

    if run.status != 'init':
        return Response({'detail': 'Invalid run status for starting.'}, status=status.HTTP_400_BAD_REQUEST)

    run.status = 'in_progress'
    run.save()
    return Response(RunSerializer(run).data, status=status.HTTP_200_OK)


@api_view(['POST'])
def stop_run_view(request, run_id):
    run = get_object_or_404(Run, id=run_id)

    if run.status != 'in_progress':
        return Response({'detail': 'Invalid run status for stopping.'}, status=status.HTTP_400_BAD_REQUEST)

    run.status = 'finished'
    run.save()
    return Response(RunSerializer(run).data, status=status.HTTP_200_OK)


class AthleteInfoView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user.id is None:
            return Response(status.HTTP_400_BAD_REQUEST)
        athlete_info, created = AthleteInfo.objects.get_or_create(user=user)
        serializer_athlete_info = AthleteInfoViewSerializer(athlete_info)
        return Response(serializer_athlete_info.data)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        athlete_info, created = AthleteInfo.objects.update_or_create(user=user, default=request.data)

        if athlete_info.weihgt <= 0 or athlete_info.weihgt >= 900:
            return Response(
                {'eror': 'Weight must be greater than 0 and less than 900.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer_athlete_info = AthleteInfoViewSerializer(athlete_info)
            return Response(serializer_athlete_info.data, status=status.HTTP_201_CREATED)
