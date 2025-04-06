from django.contrib import admin
from django.urls import path
from app_scinet.views.front_pages_view import index_page, article_page, login_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='home'),
    path('article/<int:article_id>', article_page, name='article'),
    path('login/', login_page, name='login'),

]
