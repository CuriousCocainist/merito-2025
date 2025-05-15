from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Importujesz istniejące widoki
from app_scinet.views.front_pages_view import (
    index_page, article_page, article_page_p, login_page, user_register_page,
    logout_page, like_article, unlike_article, comment_article, add_article,
    edit_profile, profile_view, edit_article, delete_article, my_articles,
    password_reset_request_view, password_reset_confirm_view, password_reset_complete_view # Dodano importy
)

# Importujesz widok zmiany hasła
from app_scinet import change_password

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='home'),
    path('article/<int:article_id>', article_page, name='article'),
    path('article-p/<int:article_id>', article_page_p, name='article_p'),
    path('register/', user_register_page, name='register'),
    path('login/', login_page, name='login'),
    path('logout/', logout_page, name='logout'),
    path('like/<int:article_id>/', like_article, name='like_article'),
    path('unlike/<int:article_id>/', unlike_article, name='unlike_article'),
    path('comment/<int:article_id>/', comment_article, name='comment_article'),
    path('article/add/', add_article, name='add_article'),
    path('articles/<int:article_id>/edit/', edit_article, name='edit_article'),
    path('articles/<int:article_id>/delete/', delete_article, name='delete_article'),
    path('profile/', profile_view, name='profile_detail'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('my-articles/', my_articles, name='my_articles'),
    # Dodajesz ścieżkę do zmiany hasła
    path('change-password/', change_password, name='change_password'),
    path('password-reset/', password_reset_request_view, name='password_reset_request'), # Dodano URL dla żądania resetu hasła
    path('password-reset/<str:token>/', password_reset_confirm_view, name='password_reset_confirm'), # Dodano URL dla potwierdzenia resetu hasła
    path('password-reset-complete/', password_reset_complete_view, name='password_reset_complete'), # Dodano URL dla zakończenia resetu hasła
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
