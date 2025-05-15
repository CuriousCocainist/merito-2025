from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    file = models.FileField(upload_to='articles_files/', blank=True, null=True)

    def __str__(self):
        return self.title