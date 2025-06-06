from django.db import models
from django.contrib.auth.models import User


def avatar_upload_path(instance, filename):
    # Funkcja do generowania ścieżki uploadu avatara: avatars/user_ID_uzytkownika/nazwa_pliku
    return f'avatars/user_{instance.user.id}/{filename}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    # DODANO: Pole do przechowywania tokenu resetowania hasła
    # Używamy blank=True i null=True, ponieważ nie każdy użytkownik będzie miał aktywny token resetu.
    # unique=True zapewnia, że każdy token jest unikalny (ważne dla bezpieczeństwa, aby uniknąć kolizji tokenów).
    reset_token = models.CharField(max_length=32, blank=True, null=True, unique=True)

    def __str__(self):
        return f"Profil użytkownika {self.user.username}"
