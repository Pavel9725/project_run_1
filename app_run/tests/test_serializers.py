from django.contrib.auth.models import User
from django.test import TestCase

from app_run.models import Run
from app_run.serializers import RunSerializer


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
            },
            {
                'id': self.run_2.id,
                'athlete': self.athlete_1.id,
                'comment': 'My 2 run!',
                'created_at': self.run_2.created_at.isoformat().replace('+00:00', 'Z'),
            },
            {
                'id': self.run_3.id,
                'athlete': self.athlete_2.id,
                'comment': '1 Run',
                'created_at': self.run_3.created_at.isoformat().replace('+00:00', 'Z'),
            },

        ]
        self.assertEqual(data, expected_data)