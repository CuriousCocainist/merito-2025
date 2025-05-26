# interactionModel.py
from django.db import models
from django.contrib.auth.models import User
from app_scinet.models.ArticleModel import Article  # <- Import Twojego modelu artykułu


# Model interakcji użytkownika z artykułem
class Interaction(models.Model):
    # Powiązanie z użytkownikiem, który wykonuje interakcję
    user = models.ForeignKey(
        User,  # Używamy wbudowanego modelu User
        on_delete=models.CASCADE,  # Usunięcie użytkownika powoduje usunięcie jego interakcji
        related_name='interactions'
    )

    # Powiązanie z artykułem
    article = models.ForeignKey(
        Article,  # Używamy Twojego modelu Article
        on_delete=models.CASCADE,  # Usunięcie artykułu usuwa jego interakcje
        related_name='interactions'
    )

    # Typ interakcji - możliwe opcje: like, comment
    INTERACTION_TYPES = [
        ('like', 'Lajk'),
        ('comment', 'Komentarz'),

    ]
    type = models.CharField(
        max_length=10,  # Krótkie pole tekstowe
        choices=INTERACTION_TYPES  # Wymusza wybór jednej z trzech opcji
    )

    # Treść interakcji - tylko dla komentarzy
    content = models.TextField(
        blank=True,  # Można pozostawić puste np. dla lajków
        null=True  # W bazie danych też może być puste
    )

    # Data utworzenia interakcji
    created_at = models.DateTimeField(
        auto_now_add=True  # Django automatycznie ustawi datę przy zapisie
    )

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.article.title}"
