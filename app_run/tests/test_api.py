from django.contrib.auth.models import User
from django.urls import reverse
from geopy.distance import geodesic, distance
from rest_framework import status
from rest_framework.test import APITestCase

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, \
    PositionSerializer, UserCollectibleItemsSerializer


class RunApiTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Admin')
        self.athlete_2 = User.objects.create(username='Kristina')
        self.athlete_3 = User.objects.create(username='Pavel')
        self.athlete_4 = User.objects.create(username='Andrey')

        self.athlete_info_1 = AthleteInfo.objects.create(user=self.athlete_1)
        self.athlete_info_2 = AthleteInfo.objects.create(user=self.athlete_2)
        self.athlete_info_3 = AthleteInfo.objects.create(user=self.athlete_3)

        self.run_1 = Run.objects.create(athlete=self.athlete_1, comment='', status='in_progress')
        self.run_2 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_3 = Run.objects.create(athlete=self.athlete_2, comment='1 Run', status='in_progress')
        self.run_4 = Run.objects.create(athlete=self.athlete_2, comment='2 Run', status='in_progress')
        self.run_5 = Run.objects.create(athlete=self.athlete_2, comment='1 Run', status='init')
        self.run_6 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_7 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_8 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_9 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_10 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_11 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_12 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_13 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_14 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='in_progress')
        self.run_15 = Run.objects.create(athlete=self.athlete_4, comment='My 2 run!', status='in_progress')
        self.run_16 = Run.objects.create(athlete=self.athlete_2, comment='My 2 run!', status='in_progress')

        self.position_1 = Position.objects.create(run=self.run_3, latitude=0.001, longitude=0.001)
        self.position_2 = Position.objects.create(run=self.run_3, latitude=0.010, longitude=0.011)
        self.position_3 = Position.objects.create(run=self.run_15, latitude=0.0012, longitude=0.0020)
        self.position_4 = Position.objects.create(run=self.run_15, latitude=0.23, longitude=0.045)
        self.position_5 = Position.objects.create(run=self.run_14, latitude=0.23, longitude=0.123)
        self.position_6 = Position.objects.create(run=self.run_14, latitude=0.0312, longitude=0.33)
        self.position_7 = Position.objects.create(run=self.run_1, latitude=0.0312, longitude=0.33)
        self.position_8 = Position.objects.create(run=self.run_16, latitude=0.5000, longitude=0.9)
        self.position_9 = Position.objects.create(run=self.run_16, latitude=0.010, longitude=0.74)

    def test_get(self):
        url = reverse('api-runs-list')
        response = self.client.get(url)
        serializer_data = RunSerializer(
            [self.run_1, self.run_2, self.run_3, self.run_4, self.run_5, self.run_6, self.run_7, self.run_8, self.run_9,
             self.run_10, self.run_11, self.run_12, self.run_13, self.run_14, self.run_15, self.run_16], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_run_id(self):
        url = reverse('api-runs-detail', args=[self.run_1.id, ])
        response = self.client.get(url)
        serializer_data = RunSerializer(self.run_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create_run(self):
        url = reverse('api-runs-list')
        data = {
            'athlete': self.athlete_1.id,
            'comment': 'Новый забег.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Run.objects.all().count(), 17)

    def test_create_run_start(self):
        run = self.run_5
        url = reverse('api-runs-start', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        run.refresh_from_db()
        self.assertEqual(run.status, 'in_progress')

    def test_create_run_start_status_not_init(self):
        run = self.run_3
        url = reverse('api-runs-start', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'detail': 'Invalid run status for starting.'}, response.data)

    def test_create_run_stop(self):
        run = self.run_3
        url = reverse('api-runs-stop', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        run.refresh_from_db()
        self.assertEqual(run.status, 'finished')

    def test_create_run_stop_create_10_challenge(self):
        self.assertEqual(Challenge.objects.filter(athlete=self.athlete_info_1).count(), 0)
        run = self.run_14
        url = reverse('api-runs-stop', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        run.refresh_from_db()
        self.assertEqual(run.status, 'finished')
        self.assertEqual(Challenge.objects.filter(athlete=self.athlete_info_1).count(), 1)

    def test_create_run_stop_create_50km_challenge(self):
        self.assertEqual(Challenge.objects.filter(athlete=self.athlete_info_2).count(), 0)
        run = self.run_16
        url = reverse('api-runs-stop', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        run.refresh_from_db()
        self.assertEqual(run.status, 'finished')
        self.assertEqual(Challenge.objects.filter(athlete=self.athlete_info_2).count(), 1)
        self.assertTrue(
            Challenge.objects.filter(athlete=self.athlete_info_2, full_name='Пробеги 50 километров!').exists())

    def test_create_run_stop_create_50km_challenge_distance_sum(self):
        run = self.run_3
        url = reverse('api-runs-stop', args=[run.id])
        distance_data = 1.493
        response = self.client.post(url, format='json')
        run.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertAlmostEqual(run.distance, distance_data, places=3)

    def test_not_athlete_info(self):
        run = self.run_15
        url = reverse('api-runs-stop', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'detail': 'AthleteInfo not found'}, response.data)

    def test_create_run_stop_status_not_init(self):
        run = self.run_5
        url = reverse('api-runs-stop', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'detail': 'Invalid run status for starting.'}, response.data)

    def test_create_run_stop_distance(self):
        run = self.run_3
        url = reverse('api-runs-stop', args=[run.id])
        distance_data = 1.493
        response = self.client.post(url, format='json')
        run.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertAlmostEqual(run.distance, distance_data, places=3)

    def test_position_2(self):
        run = self.run_1
        url = reverse('api-runs-stop', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)
        self.assertEqual({'error': 'Run stopped.  Not enough positions to calculate distance.'}, response.data)

    def test_delete_run(self):
        url = reverse('api-runs-detail', args=(self.run_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Run.objects.all().count(), 15)

    def test_get_filter_status(self):
        url = reverse('api-runs-list')
        response = self.client.get(url, data={'status': 'in_progress'})
        serializer_data = RunSerializer([self.run_1, self.run_3, self.run_4, self.run_14, self.run_15, self.run_16],
                                        many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter_athlete(self):
        url = reverse('api-runs-list')
        response = self.client.get(url, data={'athlete': self.athlete_2.id})
        serializer_data = RunSerializer([self.run_3, self.run_4, self.run_5, self.run_16], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering_created_at(self):
        url = reverse('api-runs-list')
        response = self.client.get(url, data={'ordering': 'created_at'})
        serializer_data = RunSerializer(
            [self.run_1, self.run_2, self.run_3, self.run_4, self.run_5, self.run_6, self.run_7, self.run_8, self.run_9,
             self.run_10, self.run_11, self.run_12, self.run_13, self.run_14, self.run_15, self.run_16], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


class UserApiTestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='Admin', is_superuser=True, is_staff=True)
        self.athlete_1 = User.objects.create(username='Kristina', is_staff=True, is_superuser=False)
        self.athlete_2 = User.objects.create(username='Miha', first_name='Misha', last_name='Pavioshvili',
                                             is_staff=True, is_superuser=False)
        self.athlete_3 = User.objects.create(username='Pavel', first_name='Pavel', is_staff=False, is_superuser=False)

        self.collectible_item_1 = CollectibleItem.objects.create(name='chocolate', uid='123', latitude=76.21,
                                                                 longitude=32.21, value=1, picture='www.google.com')
        self.athlete_1.collectible_items.add(self.collectible_item_1)

    def test_get_excluding_superuser(self):
        url = reverse('api-users-list')
        response = self.client.get(url)
        serializer_data = UserSerializer([self.athlete_1, self.athlete_2, self.athlete_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_coach(self):
        url = reverse('api-users-list') + '?type=coach'
        response = self.client.get(url)
        serializer_data = UserSerializer([self.athlete_1, self.athlete_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_athlete(self):
        url = reverse('api-users-list') + '?type=athlete'
        response = self.client.get(url)
        serializer_data = UserSerializer([self.athlete_3, ], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('api-users-list')
        response = self.client.get(url, data={'search': 'Pav'})
        serializer_data = UserSerializer([self.athlete_2, self.athlete_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering_date_joined(self):
        url = reverse('api-users-list')
        response = self.client.get(url, data={'ordering': 'date_joined'})
        serializer_data = UserSerializer([self.athlete_1, self.athlete_2, self.athlete_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_user_id_collectible_items(self):
        url = reverse('api-users-detail', args=(self.athlete_1.id,))
        response = self.client.get(url)
        serializer_data = UserCollectibleItemsSerializer(self.athlete_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


class AthleteInfoTestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='Admin', is_superuser=True, is_staff=True)
        self.athlete_1 = User.objects.create(username='Kristina', is_staff=True, is_superuser=False)
        self.athlete_2 = User.objects.create(username='Miha', first_name='Misha', last_name='Pavioshvili',
                                             is_staff=True, is_superuser=False)
        self.athlete_3 = User.objects.create(username='Pavel', first_name='Pavel', is_staff=False, is_superuser=False)

        self.athlete_info_1 = AthleteInfo.objects.create(user=self.athlete_1, goals='', weight=62)
        self.athlete_info_2 = AthleteInfo.objects.create(user=self.athlete_2, goals='I LOVE RUN!', weight=57)

    def test_get(self):
        url = reverse('api-athlete-info', kwargs={'user_id': self.athlete_1.id})
        response = self.client.get(url)
        serializer_data = AthleteInfoSerializer(self.athlete_info_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_put(self):
        url = reverse('api-athlete-info', kwargs={'user_id': self.athlete_1.id})
        data = {
            'goals': '',
            'weight': 62
        }
        response = self.client.put(url, data, format='json')
        serializer_data = AthleteInfoSerializer(self.athlete_info_1).data
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_put_invalid_weight(self):
        url = reverse('api-athlete-info', kwargs={'user_id': self.athlete_1.id})
        data = {
            'goals': '',
            'weight': 900
        }
        response = self.client.put(url, data, format='json')
        serializer_data = AthleteInfoSerializer(self.athlete_info_1).data
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'error': 'Invalid weight!'}, response.data)

    def test_put_weight_is_None(self):
        url = reverse('api-athlete-info', kwargs={'user_id': self.athlete_1.id})
        data = {
            'goals': '',
            'weight': None
        }
        response = self.client.put(url, data, format='json')
        serializer_data = AthleteInfoSerializer(self.athlete_info_1).data
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'error': 'Missing data!'}, response.data)

    def test_put_weight_invalid_format_weight(self):
        url = reverse('api-athlete-info', kwargs={'user_id': self.athlete_1.id})
        data = {
            'goals': '',
            'weight': 'asde'
        }
        response = self.client.put(url, data, format='json')
        serializer_data = AthleteInfoSerializer(self.athlete_info_1).data
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'error': 'Invalid weight format!'}, response.data)


class UserRunApiTestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='Admin', is_superuser=True, is_staff=True)
        self.athlete_1 = User.objects.create(username='Kristina', is_staff=True, is_superuser=False)
        self.athlete_2 = User.objects.create(username='Miha', is_staff=True, is_superuser=False)
        self.athlete_3 = User.objects.create(username='Pavel', is_staff=False, is_superuser=False)

    def test_get_excluding_superuser(self):
        url = reverse('api-users-list')
        response = self.client.get(url)
        expected_users = [self.athlete_1, self.athlete_2, self.athlete_3]
        response_data = response.data
        for user_response, user_obj in zip(response_data, expected_users):
            self.assertEqual(user_response['id'], user_obj.id)
            self.assertEqual(user_response['username'], user_obj.username)


class ChallengeTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', is_staff=True, is_superuser=False)
        self.athlete_2 = User.objects.create(username='Pavel', is_staff=True, is_superuser=False)

        self.athlete_info_1 = AthleteInfo.objects.create(user=self.athlete_1, goals='', weight=62)
        self.athlete_info_2 = AthleteInfo.objects.create(user=self.athlete_2, goals='', weight=78)

        self.challenge_1 = Challenge.objects.create(athlete=self.athlete_info_1, full_name='Сделай 10 забегов!')
        self.challenge_2 = Challenge.objects.create(athlete=self.athlete_info_1, full_name='Сделай 20 забегов!')
        self.challenge_3 = Challenge.objects.create(athlete=self.athlete_info_2, full_name='Сделай 10 забегов!')

    def test_get(self):
        url = reverse('api-challenges-list')
        response = self.client.get(url)
        serializer_data = ChallengeSerializer([self.challenge_1, self.challenge_2, self.challenge_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_athlete(self):
        url = reverse('api-challenges-list')
        response = self.client.get(url, {'athlete': self.athlete_info_1.id})
        serializer_data = ChallengeSerializer([self.challenge_1, self.challenge_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


class PositionTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', last_name='Kristina', first_name='Pyatkina')
        self.athlete_2 = User.objects.create(username='Pavel', last_name='Pavel', first_name='Grigorev')

        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='in_progress')
        self.run_2 = Run.objects.create(athlete=self.athlete_2, status='init')
        self.run_3 = Run.objects.create(athlete=self.athlete_2, status='in_progress')

        self.position_1 = Position.objects.create(run=self.run_1, latitude=0.0001, longitude=0.0002)
        self.position_2 = Position.objects.create(run=self.run_1, latitude=0.0002, longitude=0.0001)
        self.position_3 = Position.objects.create(run=self.run_1, latitude=0.0001, longitude=0.0002)
        self.position_4 = Position.objects.create(run=self.run_2, latitude=0.0000, longitude=0.0000)
        self.position_5 = Position.objects.create(run=self.run_3, latitude=0.0001, longitude=0.0001)

        self.collectible_item_1 = CollectibleItem.objects.create(name='chocolate', uid='123', latitude=76.21,
                                                                 longitude=32.21, value=1, picture='www.google.com')

    def test_get(self):
        url = reverse('api-positions-list')
        response = self.client.get(url)
        serializer_data = PositionSerializer(
            [self.position_1, self.position_2, self.position_3, self.position_4, self.position_5], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_run_id(self):
        url = reverse('api-positions-list')
        response = self.client.get(url, {'run': self.run_1.id})
        serializer_data = PositionSerializer([self.position_1, self.position_2, self.position_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_delete_position(self):
        self.assertEqual(Position.objects.all().count(), 5)
        url = reverse('api-positions-detail', args=(self.position_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Position.objects.all().count(), 4)

    def test_validate_latitude(self):
        url = reverse('api-positions-list')
        data = {
            'run': self.run_1.id,
            'latitude': -95,
            'longitude': 0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_validate_longitude(self):
        url = reverse('api-positions-list')
        data = {
            'run': self.run_1.id,
            'latitude': 0,
            'longitude': -400
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_run_position(self):
        url = reverse('api-positions-list')
        data = {
            'run': self.run_2.id,
            'latitude': 45,
            'longitude': 45
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_position(self):
        self.assertEqual(Position.objects.all().count(), 5)
        url = reverse('api-positions-list')
        data = {
            'run': self.run_3.id,
            'latitude': 45,
            'longitude': 45
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Position.objects.all().count(), 6)

    def test_get_detail(self):
        url = reverse('api-positions-detail', args=(self.position_1.id,))
        response = self.client.get(url)
        serializer_data = PositionSerializer(self.position_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update_position(self):
        url = reverse('api-positions-detail', args=(self.position_1.id,))
        data = {
            'run': self.run_1.id,
            'latitude': 10.0,
            'longitude': 20.0
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.position_1.refresh_from_db()
        self.assertEqual(self.position_1.latitude, 10.0)
        self.assertEqual(self.position_1.longitude, 20.0)

    def test_partial_update_position(self):
        url = reverse('api-positions-detail', args=(self.position_1.id,))
        data = {'latitude': 15.0}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.position_1.refresh_from_db()
        self.assertEqual(self.position_1.latitude, 15.0)

    def test_create_position_adds_collectible_items(self):
        self.assertNotIn(self.collectible_item_1, self.athlete_1.collectible_items.all())
        url = reverse('api-positions-list')
        data = {
            'run': self.run_1.id,
            'latitude': 76.21001,
            'longitude': 32.21
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.athlete_1.refresh_from_db()
        collected_items = self.athlete_1.collectible_items.all()
        self.assertIn(self.collectible_item_1, collected_items)

    def test_create_position_skips_already_collected_items(self):
        self.athlete_1.collectible_items.add(self.collectible_item_1)
        collected_ids_before = set(self.athlete_1.collectible_items.values_list('id', flat=True))
        self.assertIn(self.collectible_item_1.id, collected_ids_before)

        url = reverse('api-positions-list')
        data = {
            'run': self.run_1.id,
            'latitude': 76.21001,
            'longitude': 32.21
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.athlete_1.refresh_from_db()
        collected_ids_after = set(self.athlete_1.collectible_items.values_list('id', flat=True))

        self.assertEqual(collected_ids_before, collected_ids_after)
