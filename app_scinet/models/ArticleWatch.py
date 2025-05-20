from django.contrib.auth.models import User
from app_scinet.models.ArticleModel import Article
from django.db import models


class ArticleWatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
        verbose_name = "Article Watch"
        verbose_name_plural = "Article Watches"

    def __str__(self):
        return f"{self.user.username} watched {self.article.title}"