
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Article(models.Model):
    ACCESS_CHOICES = [
        ('public', 'Publiczny'),
        ('private', 'Prywatny'),
        ('friends', 'Tylko dla znajomych'),
    ]
    objects = None
    title = models.CharField(max_length=200)  # Pole tekstowe do 200 znaków
    content = models.TextField()  # Pole do przechowywania większego tekstu
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    file = models.FileField(
        upload_to='uploads/articles/',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        upload_to='uploads/articles/images/',
        blank=True,
        null=True,
    )
    views = models.PositiveIntegerField(
        default=0,
    )
    access_level = models.CharField(
        max_length=10,
        choices=ACCESS_CHOICES,
        default='public',
    )

    def __str__(self):
        return self.title