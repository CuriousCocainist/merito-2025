from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model # Dodano import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from app_scinet.decorators import group_required
from app_scinet.forms.ArticleForm import ArticleForm
from app_scinet.forms.CommentForm import CommentForm
from app_scinet.forms.UserProfileFrom import UserProfileForm
from app_scinet.models import Article, Interaction
from app_scinet.forms import CustomUserRegistrationForm
from app_scinet.models.UserProfileModel import UserProfile
from django import forms #Import modułu formularzy Django
from django.utils.crypto import get_random_string # Dodano import get_random_string
from django.core.mail import send_mail # Dodano import send_mail
from django.urls import reverse # Dodano import reverse
from django.contrib.sites.shortcuts import get_current_site # Dodano import get_current_site
from django.conf import settings # Dodano import settings

User = get_user_model() # Pobranie modelu User

def index_page(request):
    articles = Article.objects.all().order_by('-created_at')

    # Przechodzimy przez wszystkie artykuły pobrane wcześniej z bazy danych
    for article in articles:

        # Tworzymy nowy atrybut `like_count` w obiekcie `article`
        # Wartość to liczba interakcji typu 'like' związanych z tym artykułem
        article.like_count = Interaction.objects.filter(article=article, type='like').count()

        # Tworzymy nowy atrybut `comment_count` w obiekcie `article`
        # Wartość to liczba interakcji typu 'comment' dla tego artykułu
        article.comment_count = Interaction.objects.filter(article=article, type='comment').count()

        # Sprawdzamy, czy użytkownik jest zalogowany (czyli czy mamy dostęp do `request.user`)
        if request.user.is_authenticated:

            # Tworzymy nowy atrybut `liked_by_user` w artykule
            # Sprawdzamy, czy istnieje w bazie wpis interakcji typu 'like'
            # przypisany do tego artykułu i tego użytkownika
            article.liked_by_user = Interaction.objects.filter(
                article=article,
                user=request.user,
                type='like'
            ).exists()

        else:
            # Jeśli użytkownik nie jest zalogowany, ustawiamy `liked_by_user` na False
            article.liked_by_user = False

    # Tworzymy słownik `context`, który przekażemy do szablonu
    # Zawiera on listę artykułów z dodatkowymi atrybutami (lajki, komentarze, polubienia użytkownika)
    context = {
        'articles': articles
    }

    return render(request, 'main.html', context)


def article_page(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = Interaction.objects.filter(article=article, type='comment').order_by('created_at')
    comment_form = CommentForm()

    context = {'article': article, 'comment_form': comment_form, 'comments': comments}


    return render(request, 'article.html', context)


# PoC
@login_required
@group_required('grupa1')
def article_page_p(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    context = {'article': article}

    return render(request, 'article.html', context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        user = request.POST.get("user")
        password = request.POST.get("password")

        user = authenticate(request, username=user, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Nieprawidłowy email lub hasło.")

    return render(request, "login.html")


def user_register_page(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Ręczne tworzenie profilu
            UserProfile.objects.create(user=user)
            return redirect('home')
    else:
        form = CustomUserRegistrationForm()

    context = {'form': form}
    return render(request, 'user_register_form.html', context)


def logout_page(request):
    logout(request)
    return redirect("home")


# Widok obsługujący lajkowanie artykułu
@login_required  # Tylko zalogowany użytkownik może lajkować artykuł
def like_article(request, article_id):

    # Pobieramy artykuł, do którego użytkownik chce dodać lajka
    article = get_object_or_404(Article, pk=article_id)

    # Sprawdzamy, czy użytkownik już wcześniej polubił ten artykuł
    already_liked = Interaction.objects.filter(
        user=request.user,
        article=article,
        type='like'
    ).exists()

    # Jeśli nie ma jeszcze takiej interakcji — tworzymy nowy wpis
    if not already_liked:
        Interaction.objects.create(
            user=request.user,
            article=article,
            type='like'
        )

    # Po dodaniu lajka przekierowujemy użytkownika z powrotem na stronę główną
    return redirect('home')


@login_required
def unlike_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    # Znajdź interakcję typu 'like' dla tego użytkownika i artykułu
    like = Interaction.objects.filter(
        user=request.user,
        article=article,
        type='like'
    ).first()

    # Usuń ją jeśli istnieje
    if like:
        like.delete()

    return redirect('home')  # albo np. 'article' z powrotem



# Widok obsługujący komentowanie artykułu
@login_required
def comment_article(request, article_id):
    # Jeśli metoda jest inna niż post - przekierowanie na stronę główną
    if request.method != 'POST':
        return redirect('home')
    #jeśli nie ma takiego artykułu to 404
    article = get_object_or_404(Article, pk=article_id)
    form = CommentForm(request.POST)

    # Sprawdzamy, czy formularz jest poprawny
    if form.is_valid():
        # Jeśli formularz jest poprawny, tworzymy nową interakcję
        Interaction.objects.create(
            user=request.user,
            article=article,
            type='comment',
            # Używamy form.cleaned_data['content'], aby uzyskać treść komentarza
            #cleanded_data to słownik, który zawiera tylko poprawne dane
            #te dane są walidowane przez formularz
            content=form.cleaned_data['content']
        )
    # Po dodaniu komentarza przekierowujemy użytkownika z powrotem na stronę artykułu
    return redirect('article', article_id=article_id)


@login_required
def add_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user  # przypisywanie autora
            article.save()
            return redirect('my_articles')
    else:
        form = ArticleForm()

    return render(request, 'add_article.html', {'form': form})


@login_required
def edit_article(request, article_id):
    # Pobierz artykuł lub zwróć 404 jeśli nie istnieje lub nie należy do użytkownika
    article = get_object_or_404(Article, id=article_id, user=request.user)

    if request.method == 'POST':
        # Formularz z danymi POST i plikami, z przypisaniem do istniejącego artykułu
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('my_articles')
    else:
        # W przypadku GET — pokaż formularz z aktualnymi danymi artykułu
        form = ArticleForm(instance=article)

    return render(request, 'edit_article.html', {'form': form, 'article': article})

@login_required
def my_articles(request):
    # Pobierz parametr sortowania z URL (np. ?sort=title) lub domyślnie 'created_at'
    sort_field = request.GET.get('sort', 'created_at')
    # Pobierz kierunek sortowania ('asc' lub 'desc') lub domyślnie malejąco ('desc')
    sort_dir = request.GET.get('dir', 'desc')

    # Na podstawie kierunku sortowania ustaw prefix do sortowania (Django używa '-' dla sortowania malejącego)
    order_prefix = '-' if sort_dir == 'desc' else ''
    sort_expression = f"{order_prefix}{sort_field}"

    # Filtruj artykuły tak, aby pobrać tylko te przypisane do aktualnie zalogowanego użytkownika
    # oraz dodaj adnotacje zliczające lajki i komentarze – to działa wydajnie na poziomie bazy danych
    articles = Article.objects.filter(user=request.user)\
        .annotate(
            like_count=Count('interactions', filter=Q(interactions__type='like')),
            comment_count=Count('interactions', filter=Q(interactions__type='comment'))
        ).order_by(sort_expression)  # Sortowanie dynamiczne

    # Inicjalizacja paginacji – po 5 artykułów na stronę
    paginator = Paginator(articles, 5)
    page_number = request.GET.get('page')  # aktualny numer strony z URL
    page_obj = paginator.get_page(page_number)  # pobranie obiektów strony

    context = {
        'page_obj': page_obj,  # lista artykułów na daną stronę
        'sort': sort_field,    # przekazanie pola sortowania do szablonu
        'dir': sort_dir        # przekazanie kierunku sortowania do szablonu
    }

    return render(request, 'my_articles.html', context)



@login_required
def delete_article(request, article_id):
    # Pobierz artykuł lub zwróć 404 jeśli nie istnieje lub nie należy do użytkownika
    article = get_object_or_404(Article, id=article_id, user=request.user)

    if request.method == 'POST':
        # Po potwierdzeniu usunięcia
        article.delete()
        messages.success(request, 'Artykuł został usunięty.')
        return redirect('my_articles')

    # GET — pokaż stronę potwierdzającą usunięcie
    return render(request, 'delete_article.html', {'article': article})


@login_required  # tylko zalogowany użytkownik może uzyskać dostęp do tego widoku.
def edit_profile(request):
    # Pobiera profil użytkownika lub tworzy go, jeśli jeszcze nie istnieje.
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Tworzymy formularz na podstawie danych przesłanych metodą POST oraz przesłanych plików (avatar).
        # Ustawienie `instance=profile` powoduje, że formularz będzie edytował istniejący obiekt profilu,
        # zamiast tworzyć nowy
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Jeśli formularz jest poprawny, zapisuje dane do bazy.
            form.save()
            # Dodaje wiadomość sukcesu do systemu wiadomości Django.
            messages.success(request, "Profil został zaktualizowany.")
            # Przekierowuje z powrotem do formularza edycji (odświeżenie).
            return redirect('edit_profile')
    else:
        # Tworzy formularz z aktualnymi danymi profilu użytkownika.
        form = UserProfileForm(instance=profile)

    # Renderuje szablon z formularzem.
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def profile_view(request):
    # Pobieramy aktualnie zalogowanego użytkownika z obiektu `request`.
    user = request.user

    # Próbujemy pobrać profil użytkownika na podstawie relacji `user`.
    # Jeśli profil nie istnieje, Django zwróci błąd 404 (strona nie istnieje).
    profile = get_object_or_404(UserProfile, user=user)

    # Renderujemy szablon `profile.html`, przekazując do niego dane użytkownika i jego profil.
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile,
    })

from django import forms #Import modułu formularzy Django

class PasswordResetRequestForm(forms.Form): #Definiujemy nowy formularz do żądania resetu hasła
    email = forms.EmailField(label='Adres e-mail') #Pole na adres e-mail
    captcha = forms.CharField(label='Ile to jest 2 + 3?', max_length=5, min_length=1) # Pole na prosty test "nie jesteś robotem"

def password_reset_request_view(request): #  Definiujemy widok obsługujący żądanie resetu hasła
    if request.method == 'POST': #Sprawdzamy, czy formularz został wysłany metodą POST
        form = PasswordResetRequestForm(request.POST) # Tworzymy instancję formularza z danymi POST
        if form.is_valid(): # Sprawdzamy, czy formularz jest poprawny
            email = form.cleaned_data['email'] # Pobieramy adres e-mail z oczyszczonych danych formularza
            captcha_answer = form.cleaned_data['captcha'] # Pobieramy odpowiedź na pytanie z oczyszczonych danych

            if captcha_answer == '5': # Sprawdzamy, czy odpowiedź na pytanie jest poprawna
                try:
                    user = User.objects.get(email=email) # Pobierz użytkownika po emailu
                    token = get_random_string(length=32) # Generuj losowy token
                    profile = UserProfile.objects.get(user=user) # Pobierz profil użytkownika
                    profile.reset_token = token # Zapisz token w profilu
                    profile.save() # Zapisz zmiany w profilu

                    # Wygeneruj link do resetu hasła
                    current_site = get_current_site(request) # Pobierz aktualną domenę
                    reset_url = reverse('password_reset_confirm', kwargs={'token': token}) # Wygeneruj URL do widoku resetu
                    abs_reset_url = f'http://{current_site.domain}{reset_url}' # Skonstruuj pełny URL

                    # Wyślij email z linkiem do resetu
                    subject = 'Resetowanie hasła w SCInet' # Temat emaila
                    message = f'Kliknij w poniższy link, aby zresetować swoje hasło:\n\n{abs_reset_url}' # Treść emaila
                    from_email = settings.DEFAULT_FROM_EMAIL  # Użyj adresu z settings.py
                    recipient_list = [email] # Lista odbiorców
                    send_mail(subject, message, from_email, recipient_list) # Wyślij email

                    return render(request, 'password_reset_done.html', {'email': email}) # Renderuj stronę z potwierdzeniem
                except User.DoesNotExist: # Obsługa przypadku, gdy użytkownik nie istnieje
                    form.add_error('email', 'Nie znaleziono użytkownika z tym adresem e-mail.') # Dodaj błąd do formularza
                except UserProfile.DoesNotExist: # Obsługa przypadku, gdy profil użytkownika nie istnieje
                    form.add_error('email', 'Nie znaleziono profilu użytkownika.')
            else:
                form.add_error('captcha', 'Nieprawidłowa odpowiedź.') # Dodaj błąd do formularza
    else: # Jeśli metoda żądania to GET (użytkownik dopiero wchodzi na stronę)
        form = PasswordResetRequestForm() # Tworzymy pusty formularz

    return render(request, 'password_reset_request.html', {'form': form}) # Renderujemy formularz resetowania hasła

class SetNewPasswordForm(forms.Form): # Formularz do ustawiania nowego hasła
    password = forms.CharField(label='Nowe hasło', widget=forms.PasswordInput) # Pole na nowe hasło
    confirm_password = forms.CharField(label='Potwierdź nowe hasło', widget=forms.PasswordInput) # Pole do potwierdzenia nowego hasła

    def clean(self): # Metoda do walidacji formularza
        cleaned_data = super().clean() # Wywołaj metodę clean klasy nadrzędnej
        password = cleaned_data.get('password') # Pobierz hasło
        confirm_password = cleaned_data.get('confirm_password') # Pobierz potwierdzenie hasła

        if password and confirm_password and password != confirm_password: # Sprawdź, czy hasła się zgadzają
            raise forms.ValidationError("Hasła nie pasują do siebie.") # Jeśli nie, wyrzuć błąd

        return cleaned_data # Zwróć oczyszczone dane

def password_reset_confirm_view(request, token): # Widok do resetowania hasła po otrzymaniu tokenu
    try:
        profile = UserProfile.objects.get(reset_token=token) # Pobierz profil użytkownika po tokenie
        user = profile.user # Pobierz użytkownika z profilu
    except UserProfile.DoesNotExist: # Jeśli token jest nieprawidłowy
        return render(request, 'password_reset_failed.html') # Pokaż stronę z błędem

    if request.method == 'POST': # Jeśli formularz został wysłany
        form = SetNewPasswordForm(request.POST) # Utwórz formularz
        if form.is_valid(): # Jeśli formularz jest poprawny
            password = form.cleaned_data['password'] # Pobierz nowe hasło
            user.set_password(password) # Ustaw nowe hasło dla użytkownika
            user.save() # Zapisz zmiany
            profile.reset_token = None # Wyczyść token
            profile.save() # Zapisz zmiany w profilu
            return redirect('password_reset_complete') # Przekieruj na stronę z potwierdzeniem
    else: # Jeśli metoda to GET
        form = SetNewPasswordForm() # Utwórz pusty formularz

    return render(request, 'password_reset_confirm.html', {'form': form, 'token': token}) # Pokaż formularz resetowania hasła

def password_reset_complete_view(request):
    return render(request, 'password_reset_complete.html')
