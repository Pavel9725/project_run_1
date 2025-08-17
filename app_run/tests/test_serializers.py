from django.contrib.auth.models import User
from django.test import TestCase

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer, UserRunSerializer


class RunSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Admin')
        self.athlete_2 = User.objects.create(username='Kristina')

        self.run_1 = Run.objects.create(athlete=self.athlete_1, comment='')
        self.run_2 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!')
        self.run_3 = Run.objects.create(athlete=self.athlete_2, comment='1 Run')

    def test_ok(self):
        data = RunSerializer([self.run_1, self.run_2, self.run_3], many=True).data
        expected_data = [
            {
                'id': self.run_1.id,
                'athlete': self.athlete_1.id,
                'comment': '',
                'created_at': self.run_1.created_at.isoformat().replace('+00:00', 'Z'),
                'athlete_data': {'id': self.athlete_1.id,
                                 'username': 'Admin',
                                 'last_name': '',
                                 'first_name': ''
                                 }
            },
            {
                'id': self.run_2.id,
                'athlete': self.athlete_1.id,
                'comment': 'My 2 run!',
                'created_at': self.run_2.created_at.isoformat().replace('+00:00', 'Z'),
                'athlete_data': {'id': self.athlete_1.id,
                                 'username': 'Admin',
                                 'last_name': '',
                                 'first_name': ''
                                 }
            },
            {
                'id': self.run_3.id,
                'athlete': self.athlete_2.id,
                'comment': '1 Run',
                'created_at': self.run_3.created_at.isoformat().replace('+00:00', 'Z'),
                'athlete_data': {'id': self.athlete_2.id,
                                 'username': 'Kristina',
                                 'last_name': '',
                                 'first_name': ''
                                 }
            },

        ]
        print(f'\n\n{data}')
        self.assertEqual(data, expected_data)


class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', last_name='Kristina', first_name='Pyatkina',
                                             is_staff=True)
        self.athlete_2 = User.objects.create(username='Pavel', last_name='Pavel', first_name='Grigorev', is_staff=False)

    def test_ok(self):
        data = UserSerializer([self.athlete_1, self.athlete_2], many=True).data
        expected_data = [
            {
                'id': self.athlete_1.id,
                'date_joined': self.athlete_1.date_joined.isoformat().replace('+00:00', 'Z'),
                'username': 'Kristina',
                'last_name': 'Kristina',
                'first_name': 'Pyatkina',
                'type': 'coach'
            },
            {
                'id': self.athlete_2.id,
                'date_joined': self.athlete_2.date_joined.isoformat().replace('+00:00', 'Z'),
                'username': 'Pavel',
                'last_name': 'Pavel',
                'first_name': 'Grigorev',
                'type': 'athlete'
            },

        ]
        self.assertEqual(data, expected_data)


class UserRunSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', last_name='Kristina', first_name='Pyatkina',
                                             is_staff=True)
        self.athlete_2 = User.objects.create(username='Pavel', last_name='Pavel', first_name='Grigorev', is_staff=False)

    def test_ok(self):
        data = UserRunSerializer([self.athlete_1, self.athlete_2], many=True).data
        expected_data = [
            {
                'id': self.athlete_1.id,
                'username': 'Kristina',
                'last_name': 'Kristina',
                'first_name': 'Pyatkina',
            },
            {
                'id': self.athlete_2.id,
                'username': 'Pavel',
                'last_name': 'Pavel',
                'first_name': 'Grigorev',
            },

        ]
        self.assertEqual(data, expected_data)
