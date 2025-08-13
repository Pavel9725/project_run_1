import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_run.models import Run
from app_run.serializers import RunSerializer


class RunApiTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Admin')
        self.athlete_2 = User.objects.create(username='Kristina')
        self.athlete_3 = User.objects.create(username='Pavel')

        self.run_1 = Run.objects.create(athlete=self.athlete_1, comment='')
        self.run_2 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!')
        self.run_3 = Run.objects.create(athlete=self.athlete_2, comment='1 Run')
        self.run_4 = Run.objects.create(athlete=self.athlete_2, comment='2 Run')

    def test_get(self):
        url = reverse('api-runs-list')
        response = self.client.get(url)
        serializer_data = RunSerializer([self.run_1, self.run_2, self.run_3, self.run_4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_run_id(self):
        url = reverse('api-runs-detail', args=(self.run_1.id,))
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
        self.assertEqual(Run.objects.all().count(), 5)
