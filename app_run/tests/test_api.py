from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_run.models import Run, AthleteInfo
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer


class RunApiTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Admin')
        self.athlete_2 = User.objects.create(username='Kristina')
        self.athlete_3 = User.objects.create(username='Pavel')

        self.run_1 = Run.objects.create(athlete=self.athlete_1, comment='', status='init')
        self.run_2 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_3 = Run.objects.create(athlete=self.athlete_2, comment='1 Run', status='in_progress')
        self.run_4 = Run.objects.create(athlete=self.athlete_2, comment='2 Run', status='in_progress')
        self.run_5 = Run.objects.create(athlete=self.athlete_2, comment='1 Run', status='init')

    def test_get(self):
        url = reverse('api-runs-list')
        response = self.client.get(url)
        serializer_data = RunSerializer([self.run_1, self.run_2, self.run_3, self.run_4, self.run_5], many=True).data
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
        self.assertEqual(Run.objects.all().count(), 6)

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
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        run.refresh_from_db()
        self.assertEqual(run.status, 'finished')

    def test_create_run_stop_status_not_init(self):
        run = self.run_5
        url = reverse('api-runs-stop', args=[run.id])
        response = self.client.post(url, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'detail': 'Invalid run status for starting.'}, response.data)

    def test_delete_run(self):
        url = reverse('api-runs-detail', args=(self.run_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Run.objects.all().count(), 4)

    def test_get_filter_status(self):
        url = reverse('api-runs-list')
        response = self.client.get(url, data={'status': 'in_progress'})
        serializer_data = RunSerializer([self.run_3, self.run_4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter_athlete(self):
        url = reverse('api-runs-list')
        response = self.client.get(url, data={'athlete': self.athlete_2.id})
        serializer_data = RunSerializer([self.run_3, self.run_4, self.run_5], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering_created_at(self):
        url = reverse('api-runs-list')
        response = self.client.get(url, data={'ordering': 'created_at'})
        serializer_data = RunSerializer([self.run_1, self.run_2, self.run_3, self.run_4, self.run_5], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


class UserApiTestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='Admin', is_superuser=True, is_staff=True)
        self.athlete_1 = User.objects.create(username='Kristina', is_staff=True, is_superuser=False)
        self.athlete_2 = User.objects.create(username='Miha', first_name='Misha', last_name='Pavioshvili',
                                             is_staff=True, is_superuser=False)
        self.athlete_3 = User.objects.create(username='Pavel', first_name='Pavel', is_staff=False, is_superuser=False)

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
