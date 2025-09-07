from django.contrib.auth.models import User
from django.test import TestCase

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from app_run.serializers import RunSerializer, UserSerializer, UserRunSerializer, AthleteInfoSerializer, \
    ChallengeSerializer, PositionSerializer, CollectibleItemSerializer, UserCollectibleItemsSerializer


class RunSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Admin')
        self.athlete_2 = User.objects.create(username='Kristina')

        self.run_1 = Run.objects.create(athlete=self.athlete_1, comment='', status='init')
        self.run_2 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='init')
        self.run_3 = Run.objects.create(athlete=self.athlete_2, comment='1 Run', status='init')

    def test_ok(self):
        data = RunSerializer([self.run_1, self.run_2, self.run_3], many=True).data
        expected_data = [
            {
                'id': self.run_1.id,
                'athlete': self.athlete_1.id,
                'comment': '',
                'created_at': self.run_1.created_at.isoformat().replace('+00:00', 'Z'),
                'athlete_data': {
                    'id': self.athlete_1.id,
                    'username': 'Admin',
                    'last_name': '',
                    'first_name': ''
                },
                'status': 'init',
                'distance': None
            },
            {
                'id': self.run_2.id,
                'athlete': self.athlete_1.id,
                'comment': 'My 2 run!',
                'created_at': self.run_2.created_at.isoformat().replace('+00:00', 'Z'),
                'athlete_data': {
                    'id': self.athlete_1.id,
                    'username': 'Admin',
                    'last_name': '',
                    'first_name': ''
                },
                'status': 'init',
                'distance': None
            },
            {
                'id': self.run_3.id,
                'athlete': self.athlete_2.id,
                'comment': '1 Run',
                'created_at': self.run_3.created_at.isoformat().replace('+00:00', 'Z'),
                'athlete_data': {
                    'id': self.athlete_2.id,
                    'username': 'Kristina',
                    'last_name': '',
                    'first_name': ''
                },
                'status': 'init',
                'distance': None
            },

        ]
        self.assertEqual(data, expected_data)


class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', last_name='Kristina', first_name='Pyatkina',
                                             is_staff=True)
        self.athlete_2 = User.objects.create(username='Pavel', last_name='Pavel', first_name='Grigorev', is_staff=False)

        self.run_1 = Run.objects.create(athlete=self.athlete_1, comment='', status='init')
        self.run_2 = Run.objects.create(athlete=self.athlete_1, comment='My 2 run!', status='finished')
        self.run_3 = Run.objects.create(athlete=self.athlete_2, comment='1 Run', status='init')

    def test_ok(self):
        data = UserSerializer([self.athlete_1, self.athlete_2], many=True).data
        expected_data = [
            {
                'id': self.athlete_1.id,
                'date_joined': self.athlete_1.date_joined.isoformat().replace('+00:00', 'Z'),
                'username': 'Kristina',
                'last_name': 'Kristina',
                'first_name': 'Pyatkina',
                'type': 'coach',
                'runs_finished': 1
            },
            {
                'id': self.athlete_2.id,
                'date_joined': self.athlete_2.date_joined.isoformat().replace('+00:00', 'Z'),
                'username': 'Pavel',
                'last_name': 'Pavel',
                'first_name': 'Grigorev',
                'type': 'athlete',
                'runs_finished': 0
            },

        ]
        self.assertEqual(data, expected_data)


class UserCollectibleItemsSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', last_name='Kristina', first_name='Pyatkina',
                                             is_staff=True)

        self.collectible_item_1 = CollectibleItem.objects.create(
            name='Item 1',
            uid='uid1',
            latitude=10.0,
            longitude=20.0,
            picture='http://example.com/pic1.jpg',
            value=5
        )
        self.collectible_item_2 = CollectibleItem.objects.create(
            name='Item 2',
            uid='uid2',
            latitude=11.0,
            longitude=21.0,
            picture='http://example.com/pic2.jpg',
            value=10
        )

        self.athlete_1.collectible_items.add(self.collectible_item_1, self.collectible_item_2)

    def test_ok(self):
        data = UserCollectibleItemsSerializer(self.athlete_1).data

        expected_items = [
            {
                'id': self.collectible_item_1.id,
                'name': self.collectible_item_1.name,
                'uid': self.collectible_item_1.uid,
                'latitude': self.collectible_item_1.latitude,
                'longitude': self.collectible_item_1.longitude,
                'picture': self.collectible_item_1.picture,
                'value': self.collectible_item_1.value,
            },
            {
                'id': self.collectible_item_2.id,
                'name': self.collectible_item_2.name,
                'uid': self.collectible_item_2.uid,
                'latitude': self.collectible_item_2.latitude,
                'longitude': self.collectible_item_2.longitude,
                'picture': self.collectible_item_2.picture,
                'value': self.collectible_item_2.value,
            }
        ]

        expected_data = {
            'id': self.athlete_1.id,
            'username': self.athlete_1.username,
            'first_name': self.athlete_1.first_name,
            'last_name': self.athlete_1.last_name,
            'email': self.athlete_1.email,
            'items': expected_items,
        }

        for field in UserCollectibleItemsSerializer.Meta.fields:
            self.assertIn(field, data)

        self.assertEqual(data['items'], expected_items)


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


class AthleteInfoSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', last_name='Kristina', first_name='Pyatkina')
        self.athlete_info_1 = AthleteInfo.objects.create(user=self.athlete_1, goals='Love Run!', weight=56)

    def test_ok(self):
        data = AthleteInfoSerializer([self.athlete_info_1, ], many=True).data
        expected_data = [
            {
                'id': self.athlete_info_1.id,
                'goals': 'Love Run!',
                'weight': 56,
            },
        ]
        self.assertEqual(data, expected_data)


class ChallengeSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', last_name='Kristina', first_name='Pyatkina')
        self.athlete_info_1 = AthleteInfo.objects.create(user=self.athlete_1, goals='Love Run!', weight=56)
        self.challenge_1 = Challenge.objects.create(athlete=self.athlete_info_1, full_name='Сделай 10 забегов!')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='init')

    def test_ok(self):
        data = ChallengeSerializer([self.challenge_1, ], many=True).data
        expected_data = [
            {
                'athlete': self.athlete_1.id,
                'full_name': 'Сделай 10 забегов!',

            },
        ]
        self.assertEqual(data, expected_data)


class PositionsSerializerTestCase(TestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='Kristina', last_name='Kristina', first_name='Pyatkina')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='init')
        self.position_1 = Position.objects.create(run=self.run_1, latitude=0.0001, longitude=0.0001)

    def test_ok(self):
        data = PositionSerializer([self.position_1, ], many=True).data
        expected_data = [
            {
                'id': self.position_1.id,
                'run': self.run_1.id,
                'latitude': 0.0001,
                'longitude': 0.0001,

            },
        ]
        self.assertEqual(data, expected_data)


class CollectibleItemsSerializerTestCase(TestCase):
    def setUp(self):
        self.collectible_item_1 = CollectibleItem.objects.create(
            name='Test Item',
            uid='unique123',
            latitude=55.7558,
            longitude=37.6173,
            picture='http://example.com/pic.jpg',
            value=10
        )

    def test_ok(self):
        data = CollectibleItemSerializer([self.collectible_item_1], many=True).data

        expected_data = [
            {
                'id': self.collectible_item_1.id,
                'name': 'Test Item',
                'uid': 'unique123',
                'latitude': 55.7558,
                'longitude': 37.6173,
                'picture': 'http://example.com/pic.jpg',
                'value': 10,
            },
        ]
        self.assertEqual(data, expected_data)
