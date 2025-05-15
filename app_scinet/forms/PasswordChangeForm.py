from django import forms  # Importujemy moduł do tworzenia formularzy w Django

# Tworzymy klasę formularza do zmiany hasła, dziedziczącą z base forms.Form
class PasswordChangeForm(forms.Form):
    # Pole na wpisanie aktualnego hasła, ukryte (PasswordInput), z odpowiednim etykietą
    old_password = forms.CharField(
        widget=forms.PasswordInput,  # Ukrywa wpisywane hasło
        label="Aktualne hasło"      # Etykieta wyświetlana użytkownikowi
    )
    # Pole na nowe hasło, ukryte, z własną etykietą
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Nowe hasło"
    )
    # Pole na powtórne wpisanie nowego hasła, ukryte, z własną etykietą
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Powtórz Nowy hasło"
    )

    # Konstruktor klasy, przyjmuje użytkownika i inne argumenty
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Wywołanie konstruktora bazowej klasy
        self.user = user  # Przechowujemy użytkownika, aby mieć dostęp do niego w metodach walidacji

    # Metoda do oczyszczania i walidacji danych formularza
    def clean(self):
        # Wywołujemy bazową metodę clean() i pobieramy dane po wstępnej walidacji
        cleaned_data = super().clean()

        # Pobieramy wpisane dane z pól formularza
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Sprawdzamy, czy podane stare hasło jest poprawne dla aktualnego użytkownika
        if not self.user.check_password(old_password):
            # Jeśli nie, dodajemy błąd do pola 'old_password'
            self.add_error('old_password', 'Niepoprawne aktualne hasło.')

        # Sprawdzamy, czy dwa wpisy nowego hasła się zgadzają
        if new_password != confirm_password:
            # Jeśli nie, dodajemy błąd do pola 'confirm_password'
            self.add_error('confirm_password', 'Hasła do siebie nie pasują.')

        # Sprawdzamy, czy nowe hasło nie jest takie samo jak stare
        if old_password and new_password and old_password == new_password:
            # Jeśli tak, dodajemy błąd do pola 'new_password'
            self.add_error('new_password', 'Nowe hasło nie może być takie samo jak stare.')

        # Dodatkowo sprawdzamy, czy nowe hasło spełnia podstawowe zasady (np. długość)
        if new_password and len(new_password) <= 8:
            # Jeśli hasło jest krótsze niż 8 znaków, to błąd
            self.add_error('new_password', 'Hasło musi mieć przynajmniej 8 znaków.')