from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Min, Max, Count, Q, Avg
from django.shortcuts import get_object_or_404
from django_filters import NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from geopy.distance import geodesic
from openpyxl import load_workbook
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView


from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem, Subscribe
from app_run.serializers import RunSerializer, UserSerializers, AthleteInfoViewSerializer, ChallengeSerializer, \
    PositionSerializer, CollectibleItemSerializer, UserAthleteCollectibleItemSerializers, \
    UserCoachCollectibleItemSerializers, AthleteSummarySerializer


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_superuser=False).annotate(
        runs_finished=Count('runs', filter=Q(runs__status='finished')),
        rating=Avg('subscribe_coach__rating')
    )
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

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializers
        elif self.action == 'retrieve':
            user = self.get_object()
            if user.is_staff:
                return UserCoachCollectibleItemSerializers
            else:
                return UserAthleteCollectibleItemSerializers
        return super().get_serializer_class()


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

        positions = list(run.positions.order_by('id'))
        total_distance = 0.0

        run.status = 'finished'
        if len(positions) > 2:
            for i in range(len(positions) - 1):
                start = (positions[i].latitude, positions[i].longitude)
                end = (positions[i + 1].latitude, positions[i + 1].longitude)
                total_distance += geodesic(start, end).kilometers
        run.distance = round(total_distance, 3)

        run.save()

        user = run.athlete

        try:
            athlete_info = user.athlete_info
        except ObjectDoesNotExist:
            athlete_info = AthleteInfo.objects.create(user=user)

        finished_run_count = Run.objects.filter(athlete=user, status='finished').count()

        if finished_run_count == 10:
            if not Challenge.objects.filter(full_name='Сделай 10 Забегов!', athlete=athlete_info).exists():
                Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=athlete_info)

        sum_run_distance = Run.objects.filter(athlete=user, status='finished').aggregate(total=Sum('distance'))[
                               'total'] or 0

        if sum_run_distance >= 50:
            if not Challenge.objects.filter(full_name='Пробеги 50 километров!', athlete=athlete_info).exists():
                Challenge.objects.create(full_name='Пробеги 50 километров!', athlete=athlete_info)

        if run.distance >= 2.0 and run.run_time_seconds is not None and run.run_time_seconds <= 600:
            if not Challenge.objects.filter(full_name='2 километра за 10 минут!', athlete=athlete_info).exists():
                Challenge.objects.create(full_name='2 километра за 10 минут!', athlete=athlete_info)

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
        athlete_info, created = AthleteInfo.objects.get_or_create(user=user)
        serializer_athlete_info = AthleteInfoViewSerializer(athlete_info)
        return Response(serializer_athlete_info.data)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        data = request.data.copy()

        weight_value = data.get('weight')
        if weight_value is not None:
            try:
                weight_int = int(weight_value)
                data['weight'] = weight_int
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Weight must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
        athlete_info, created = AthleteInfo.objects.update_or_create(user=user, defaults=request.data)

        weight = int(athlete_info.weight)
        if weight is None or weight <= 0 or weight >= 900:
            return Response(
                {'error': 'Weight must be greater than 0 and less than 900.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer_athlete_info = AthleteInfoViewSerializer(athlete_info)
        return Response(serializer_athlete_info.data, status=status.HTTP_201_CREATED)


class Athlete_infoViewSet(viewsets.ModelViewSet):
    queryset = AthleteInfo.objects.all()
    serializer_class = AthleteInfoViewSerializer


class ChallengeFilter(filters.FilterSet):
    athlete = NumberFilter(field_name='athlete__user__id')

    class Meta:
        model = Challenge
        fields = ['athlete']


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.select_related('athlete__user').all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChallengeFilter


class PositionFilter(filters.FilterSet):
    run = NumberFilter(field_name='run__id')

    class Meta:
        model = Position
        fields = ['run']


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.select_related('run__athlete').all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PositionFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        position = self.perform_create(serializer)

        athlete = position.run.athlete
        coordinate_athlete = (position.latitude, position.longitude)

        items = CollectibleItem.objects.all()

        for item in items:
            coordinate_item = (item.latitude, item.longitude)
            distance_m = geodesic(coordinate_athlete, coordinate_item).meters

            if distance_m <= 100:
                if not item.collected_by.filter(id=athlete.id).exists():
                    item.collected_by.add(athlete)

        run = position.run
        run_agg = run.positions.aggregate(
            min_time=Min('date_time'),
            max_time=Max('date_time')
        )
        min_time = run_agg['min_time']
        max_time = run_agg['max_time']

        if min_time and max_time:
            run_time = max_time - min_time
            run.run_time_seconds = int(run_time.total_seconds())
            run.save(update_fields=['run_time_seconds'])
        run_serializer = RunSerializer(run)
        return Response(run_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        position = serializer.save()

        run = position.run

        prev_position = run.positions.filter(date_time__lt=position.date_time).last()

        if prev_position is None:
            position.speed = 0.0
            position.distance = 0.0
        else:
            coordinate_prev = (prev_position.latitude, prev_position.longitude)
            coordinate_curr = (position.latitude, position.longitude)
            dist = geodesic(coordinate_prev, coordinate_curr).meters

            delta_sec = (position.date_time - prev_position.date_time).total_seconds()
            dist_km = dist / 1000
            speed = dist / delta_sec if delta_sec > 0 else 0.0

            total_distance = prev_position.distance + dist_km
            position.speed = round(speed, 2)
            position.distance = round(total_distance, 2)

        position.save(update_fields=['speed', 'distance'])

        average_speed = round((run.positions.aggregate(average_speed=Avg('speed'))['average_speed'] or 0), 2)
        run.speed = average_speed
        run.save(update_fields=['speed'])

        return position


class CollectibleItemViewSet(viewsets.ModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer


class UploadFileView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get('file')

        # uploaded_file = load_workbook('C:/Users/pyatk/Downloads/upload_example.xlsx')

        if uploaded_file is None:
            return Response({'error': 'File not found.'}, status=status.HTTP_400_BAD_REQUEST)

        file_data = load_workbook(uploaded_file)

        # ws = uploaded_file.active
        ws = file_data.active
        rows = list(ws.iter_rows(min_row=2, values_only=True))

        valid_data = []
        invalid_data = []

        for row in rows:
            data = {
                'name': row[0],
                'uid': row[1],
                'value': row[2],
                'latitude': row[3],
                'longitude': row[4],
                'picture': row[5]
            }
            serializer = CollectibleItemSerializer(data=data)

            if serializer.is_valid():
                valid_data.append(serializer)
            else:
                invalid_data.append(list(row))

        for serializer in valid_data:
            serializer.save()
        return Response(invalid_data, status=status.HTTP_200_OK)


class SubscribeToCoachView(APIView):
    def post(self, request, id):
        coach = get_object_or_404(User, id=id)

        if not coach.is_staff:
            return Response({'detail': 'User not coach!'}, status=status.HTTP_400_BAD_REQUEST)

        athlete_id = request.data.get('athlete')
        if athlete_id is None:
            return Response({'detail': 'User id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            athlete = User.objects.get(id=athlete_id)
        except User.DoesNotExist:
            return Response({'detail': 'Athlete not found'}, status=status.HTTP_400_BAD_REQUEST)

        if Subscribe.objects.filter(coach=coach, athlete=athlete).exists():
            return Response({'detail': 'Subscription already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if athlete.is_staff:
            return Response({'detail': 'Coach not subscribe!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Subscribe.objects.create(coach=coach, athlete=athlete)

        return Response({'detail': 'Subscribed successfully'}, status=status.HTTP_200_OK)


class ChallengesSummaryAPIView(APIView):
    def get(self, request):
        challenge_names = Challenge.objects.values_list('full_name', flat=True).distinct()
        athletes_qs = AthleteInfo.objects.select_related('user')

        result = []

        for ch in challenge_names:
            athletes_for_challenge = athletes_qs.filter(challenges__full_name=ch).distinct()
            athletes_serializer = AthleteSummarySerializer(athletes_for_challenge, many=True).data
            result.append({
                'name_to_display': ch,
                'athletes': athletes_serializer
            })
        return Response(result)


class RateCoachView(APIView):
    def post(self, request, coach_id):
        coach = get_object_or_404(User, id=coach_id)
        athlete_id = request.data.get('athlete')
        rating = request.data.get('rating')

        if not coach.is_staff:
            return Response({'detail': 'User not coach!'}, status=status.HTTP_400_BAD_REQUEST)
        if athlete_id is None:
            return Response({'detail': 'User id is required'}, status=status.HTTP_400_BAD_REQUEST)
        if rating < 1 or rating > 5:
            return Response({'detail': 'Rating must be between 1 and 5!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            athlete = User.objects.get(id=athlete_id)
        except User.DoesNotExist:
            return Response({'detail': 'Athlete not found'}, status=status.HTTP_400_BAD_REQUEST)

        if athlete.is_staff:
            return Response({'detail': 'Coach not subscribe!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subscription = Subscribe.objects.get(coach=coach, athlete=athlete)
        except Subscribe.DoesNotExist:
            return Response({'detail': 'Athlete must be subscribe to coach to rate'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.rating = rating
        subscription.save()

        return Response({'detail': 'Subscribed successfully'}, status=status.HTTP_200_OK)
