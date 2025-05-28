from django.db import models
from django.contrib.auth.models import User

class FriendshipModel(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Oczekujące'),
        ('accepted', 'Zaakceptowane'),
        ('declined', 'Odrzucone'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friend_requests_sent'
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friend_requests_received'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username} ({self.get_status_display()})"