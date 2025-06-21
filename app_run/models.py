from django.contrib.auth.models import User
from django.db import models


class Run(models.Model):
    STATUS_CHOICES = [
        ('init', 'Initialization'),
         ('in_progress', 'In_progress'),
         ('finished', 'Finished')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='init')

    def __str__(self):
        return f'{self.athlete}'
