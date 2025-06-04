from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect  # Funkcja do renderowania stron i przekierowań
from django.contrib.auth.decorators import login_required  # Dekorator, który wymaga logowania użytkownika
from django.contrib.auth import update_session_auth_hash  # Funkcja, która odświeża sesję po zmianie hasła
from django.contrib import messages  # Funkcja do wyświetlania komunikatów dla użytkownika
from .forms.PasswordChangeForm import PasswordChangeForm  # Twój własny formularz do zmiany hasła
from django.db.models import Q
from django.contrib.auth.models import User

from .models.FriendshipModel import FriendshipModel


@login_required  # Umożliwia dostęp tylko zalogowanym użytkownikom
def change_password(request):
    if request.method == 'POST':  # Jeśli użytkownik wysłał formularz
        form = PasswordChangeForm(request.user, request.POST)  # Tworzymy formularz z danymi i przekazujemy użytkownika
        if form.is_valid():  # Jeśli dane są poprawne
            # Zmieniamy hasło użytkownika na nowe
            user = request.user
            user.set_password(form.cleaned_data['new_password'])  # Ustawiamy nowe hasło
            user.save()  # Zapisujemy użytkownika z nowym hasłem

            # Odświeżamy sesję, żeby użytkownik nie został wylogowany po zmianie hasła
            update_session_auth_hash(request, user)

            # Wyświetlamy komunikat o sukcesie
            messages.success(request, 'Twoje hasło zostało pomyślnie zmienione!')

            # Przekierowujemy na stronę profilu lub inną (np. homepage)
            return redirect('profile')  # Upewnij się, że masz taką nazwę URL w pliku urls.py
    else:
        # Jeśli to jest pierwszy dostęp (GET), pokazujemy pusty formularz
        form = PasswordChangeForm(request.user)
    # Renderujemy szablon, do którego przekazujemy formularz
    return render(request, 'change_password.html', {'form': form})


def get_suggested_users(request):
    if request.user.is_authenticated:
        # Pobierz wszystkich użytkowników oprócz siebie
        all_users = User.objects.exclude(id=request.user.id)

        # Pobierz ID użytkowników, którzy są już znajomymi lub mają oczekujące zaproszenia
        excluded_ids = set()

        # Dodaj ID z zaakceptowanych znajomości
        friendships = FriendshipModel.objects.filter(
            (Q(user=request.user) | Q(friend=request.user)),
            status='accepted'
        )

        # Dodaj ID z oczekujących zaproszeń
        pending_requests = FriendshipModel.objects.filter(
            (Q(user=request.user) | Q(friend=request.user)),
            status='pending'
        )

        # Zbierz wszystkie ID do wykluczenia
        for friendship in friendships:
            if friendship.user == request.user:
                excluded_ids.add(friendship.friend.id)
            else:
                excluded_ids.add(friendship.user.id)

        for request in pending_requests:
            if request.user == request.user:
                excluded_ids.add(request.friend.id)
            else:
                excluded_ids.add(request.user.id)

        # Wyklucz już dodanych znajomych i oczekujące zaproszenia
        # Sortuj po dacie dołączenia (od najnowszych) i ogranicz do 5 wyników
        suggested_users = all_users.exclude(
            id__in=excluded_ids
        ).order_by('-date_joined')[:5]

        return suggested_users
    return User.objects.none()
