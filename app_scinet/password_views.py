from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect  # Funkcja do renderowania stron i przekierowań
from django.contrib.auth.decorators import login_required  # Dekorator, który wymaga logowania użytkownika
from django.contrib.auth import update_session_auth_hash  # Funkcja, która odświeża sesję po zmianie hasła
from django.contrib import messages  # Funkcja do wyświetlania komunikatów dla użytkownika
from .forms.PasswordChangeForm import PasswordChangeForm  # Twój własny formularz do zmiany hasła


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