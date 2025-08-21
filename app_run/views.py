from email.policy import default

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Run, AthleteInfo
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer


@api_view(['GET'])
def view_about(request):
    details = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS
    }
    return Response(details)


class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50


class UserPagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    pagination_class = RunPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    ordering = ['id']  # Сортировка по умолчанию


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type')
        if type == 'coach':
            qs = qs.filter(is_staff=True)
        if type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class RunStartAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)

        if run.status != 'init':
            return Response({'detail': 'Invalid run status for starting.'}, status=status.HTTP_400_BAD_REQUEST)

        run.status = 'in_progress'
        run.save()

        return Response(RunSerializer(run).data, status=status.HTTP_201_CREATED)


class RunStopAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)

        if run.status != 'in_progress':
            return Response({'detail': 'Invalid run status for starting.'}, status=status.HTTP_400_BAD_REQUEST)

        run.status = 'finished'
        run.save()

        return Response(RunSerializer(run).data, status=status.HTTP_201_CREATED)


class AthleteInfoView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        athlete, created = AthleteInfo.objects.get_or_create(user=user)
        serializer = AthleteInfoSerializer(athlete)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        weight = request.data.get('weight')
        goals = request.data.get('goals')

        if weight is None or goals is None:
            return Response({'error': 'Missing data!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            weight = int(weight)
        except ValueError:
            return Response({'error': 'Invalid weight format!'}, status=status.HTTP_400_BAD_REQUEST)

        if weight <= 0 or weight >= 900:
            return Response({'error': 'Invalid weight!'}, status=status.HTTP_400_BAD_REQUEST)

        athlete, created = AthleteInfo.objects.update_or_create(user=user,
                                                                defaults={
                                                                    'weight': weight,
                                                                    'goals': goals
                                                                })
        serializer = AthleteInfoSerializer(athlete)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
