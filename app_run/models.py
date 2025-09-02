from django.contrib.auth.models import User
from django.db import models


class Run(models.Model):
    STATUS_CHOICES = (
        ('init', 'Init'),
        ('in_progress', 'In_progress'),
        ('finished', 'Finished'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='runs')
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='init')
    distance = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'Id:{self.id} athlete: {self.athlete} athlete_id: {self.athlete.id} {self.status}'

class AthleteInfo(models.Model):
    goals = models.CharField(max_length=255)
    weight = models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'user:{self.user}'

class Challenge(models.Model):
    full_name = models.CharField(max_length=255)
    athlete = models.ForeignKey(AthleteInfo, on_delete=models.CASCADE, related_name='challenges')

    def __str__(self):
        return f'full_name:{self.full_name}, athlete:{self.athlete}'

class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='positions')
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f'run:{self.run}'

class CollectibleItem(models.Model):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    picture = models.URLField()
    value = models.IntegerField()