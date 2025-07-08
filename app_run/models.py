from django.contrib.auth.models import User
from django.db import models
from geopy.distance import geodesic


class Run(models.Model):
    STATUS_CHOICES = [
        ('init', 'Initialization'),
        ('in_progress', 'In_progress'),
        ('finished', 'Finished')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='runs')
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='init')
    distance = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'athlete_id: {self.athlete.id} id:{self.id} {self.status}'


class AthleteInfo(models.Model):
    goals = models.TextField(blank=True, default='')
    weight = models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_info')

    def __str__(self):
        return f'{self.user} user.id: {self.user.id} athlete.id: {self.id}'


class Challenge(models.Model):
    full_name = models.CharField(max_length=255)
    athlete = models.ForeignKey(AthleteInfo, on_delete=models.CASCADE, related_name='challenges')

    def __str__(self):
        return f'{self.full_name} athlete: {self.athlete}'


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='positions')
    latitude = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    longitude = models.DecimalField(max_digits=8, decimal_places=4, default=0)
