from django.contrib.auth.models import User
from django.db import models


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

    def __str__(self):
        return f'{self.athlete}'

class AthleteInfo(models.Model):
    goals = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_info')
