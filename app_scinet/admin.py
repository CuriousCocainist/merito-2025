from django.contrib import admin
from app_scinet.models import Article
from app_scinet.models.UserProfileModel import UserProfile

# Register your models here.
admin.site.register(Article)
admin.site.register(UserProfile)