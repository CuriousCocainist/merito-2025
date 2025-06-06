from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views # <-- Import wbudowanych widoków autoryzacji Django


# Import wszystkich widoków z app_scinet.views.front_pages_view
from app_scinet.views.front_pages_view import (
    index_page, article_page, article_page_p, login_page, user_register_page,
    logout_page, like_article, unlike_article, comment_article, add_article,
    edit_profile, profile_view, edit_article, user_profile_view,
    delete_article, my_articles, send_friend_request, accept_friend_request,
    decline_friend_request, friends_list, search,
    follow_article, unfollow_article, followed_articles,
    cancel_friend_request, # Dodano cancel_friend_request, jeśli jest używane
    conversation_view, conversation_list_view,
    password_reset_request_view, password_reset_complete_view, password_reset_confirm_view
)

# Import widoków zmiany hasła
from app_scinet.password_views import change_password

# Import widoków pobierania plików
from app_scinet.download_view import download_article_file as scinet_download_article_file


urlpatterns = [
    path('admin/', admin.site.urls), # Panel administratora Django

    # --- URL-e Główne i Artykuły ---
    path('', index_page, name='home'), # Strona główna
    path('article/<int:article_id>/', article_page, name='article'), # Widok artykułu dostępny dla wszystkich
    path('article-p/<int:article_id>/', article_page_p, name='article_p'), # Widok artykułu dostępny tylko dla zalogowanych
    path('article/add/', add_article, name='add_article'), # Dodawanie artykułu
    path('articles/<int:article_id>/edit/', edit_article, name='edit_article'), # Edycja artykułu
    path('articles/<int:article_id>/delete/', delete_article, name='delete_article'), # Usunięcie artykułu
    path('my-articles/', my_articles, name='my_articles'), # Wyświetlenie własnych publikacji
    path('article/<int:article_id>/download/', scinet_download_article_file, name='download_article_file'), # Pobieranie pliku
    path('search/', search, name='search'), # Wyszukiwarka

    # --- URL-e Uwierzytelniania i Zarządzania Kontem ---
    path('register/', user_register_page, name='register'), # Rejestracja nowego użytkownika
    path('login/', login_page, name='login'), # Logowanie
    path('logout/', logout_page, name='logout'), # Wylogowanie
    path('profile/', profile_view, name='profile_detail'), # Podgląd własnego profilu
    path('profile/<int:user_id>/', user_profile_view, name='user_profile_view'), # Podgląd profilu innego użytkownika
    path('profile/edit/', edit_profile, name='edit_profile'), # Edycja profilu
    path('change-password/', change_password, name='change_password'), # Zmiana hasła dla zalogowanego użytkownika

    # --- URL-e do Resetowania Hasła (dla niezalogowanych użytkowników) ---
    path('password-reset/', password_reset_request_view, name='password_reset_request'),
    path('password-reset/<str:uidb64>/<str:token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('password-reset-complete/', password_reset_complete_view, name='password_reset_complete'),


    # --- URL-e Interakcji Społecznościowych (Lajki, Komentarze, Obserwowanie) ---
    path('like/<int:article_id>/', like_article, name='like_article'), # Polubienie artykułu
    path('unlike/<int:article_id>/', unlike_article, name='unlike_article'), # Usunięcie polubienia
    path('comment/<int:article_id>/', comment_article, name='comment_article'), # Dodanie komentarza
    path('follow/<int:article_id>/', follow_article, name='follow_article'), # Obserwacja artykułu
    path('unfollow/<int:article_id>/', unfollow_article, name='unfollow_article'), # Odobserwowanie artykułu
    path('followed-articles/', followed_articles, name='followed_articles'), # Obserwowane artykuły

    # --- URL-e Zarządzania Znajomymi ---
    path('send-request/<int:user_id>/', send_friend_request, name='send_friend_request'), # Wysłanie zaproszenia
    path('accept-request/<int:request_id>/', accept_friend_request, name='accept_friend_request'), # Akceptacja zaproszenia
    path('decline-request/<int:request_id>/', decline_friend_request, name='decline_friend_request'), # Odrzucenie zaproszenia
    path('cancel-request/<int:user_id>/', cancel_friend_request, name='cancel_friend_request'), # Anulowanie zaproszenia
    path('friends/', friends_list, name='friends_list'), # Wyświetlenie listy znajomych

    # --- URL-e Modułu Wiadomości ---
    path('conversations/', conversation_list_view, name='conversation'), # Wyświetlenie listy rozmów
    path('conversation/<int:user_id>/', conversation_view, name='conversation'), # Widok pojedynczej rozmowy
    path('conversations/', conversation_list_view, name='conversation_list'),

]

# W trybie DEBUG pozwalamy na wyświetlanie przesłanych plików (np. zdjęć)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
