from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model # Dodano import get_user_model
ib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from app_scinet.decorators import group_required
from app_scinet.forms.ArticleForm import ArticleForm
from app_scinet.forms.CommentForm import CommentForm
from app_scinet.forms.UserProfileFrom import UserProfileForm
from app_scinet.models import Article, Interaction, ArticleWatch
from app_scinet.forms import CustomUserRegistrationForm
from app_scinet.models.FriendshipModel import FriendshipModel
from app_scinet.models.UserProfileModel import UserProfile
from django import forms #Import modułu formularzy Django
from django.utils.crypto import get_random_string # Dodano import get_random_string
from django.core.mail import send_mail # Dodano import send_mail
from django.urls import reverse # Dodano import reverse
from django.contrib.sites.shortcuts import get_current_site # Dodano import get_current_site
from django.conf import settings # Dodano import settings

User = get_user_model() # Pobranie modelu User

def get_article_related_details(request, article):
    if request.user.is_authenticated:
        # Sprawdzenie, czy zalogowany użytkownik polubił artykuł
        article.liked_by_user = Interaction.objects.filter(
            article=article,
            user=request.user,
            type='like'
        ).exists()

        # Sprawdzenie, czy zalogowany użytkownik śledzi artykuł
        article.followed_by_user = ArticleWatch.objects.filter(
            article=article,
            user=request.user
        ).exists()
    else:
        # Jeśli użytkownik nie jest zalogowany, ustawiamy `liked_by_user` na False
        article.liked_by_user = False
        # Jeśli użytkownik nie jest zalogowany, ustawiamy `followed_by_user` na False
        article.followed_by_user = False

def index_page(request):
    if request.user.is_authenticated:
        # Szukamy wszystkich zaakceptowanych znajomości w obie strony
        accepted_friendships = FriendshipModel.objects.filter(
            Q(user=request.user) | Q(friend=request.user),
            status='accepted'
        )

        # Wyciągamy ID znajomych
        friend_ids = set()
        for friendship in accepted_friendships:
            if friendship.user == request.user:
                friend_ids.add(friendship.friend.id)
            else:
                friend_ids.add(friendship.user.id)

        # Filtrujemy artykuły
        articles_list = Article.objects.filter(
            Q(access_level='public') |
            Q(access_level='private', user=request.user) |
            Q(access_level='friends', user__id__in=friend_ids)
        ).order_by('-created_at')
    else:
        # Tylko publiczne dla niezalogowanych
        articles_list = Article.objects.filter(access_level='public').order_by('-created_at')

    # Inicjalizacja mechanizmu paginacji z limitem 5 artykułów na stronę
    paginator = Paginator(articles_list, 5)

    # Pobranie numeru bieżącej strony z parametrów GET w żądaniu
    page_number = request.GET.get('page')

    # Uzyskanie obiektu strony korzystając z paginatora
    page_obj = paginator.get_page(page_number)

    # Dla każdego artykułu na liście, liczy ile polubień i komentarzy ma artykuł
    # oraz sprawdza, czy zalogowany użytkownik polubił dany artykuł
    for article in page_obj:
        # Zliczanie polubień dla każdego artykułu
        article.like_count = Interaction.objects.filter(article=article, type='like').count()

        # Zliczanie komentarzy dla każdego artykułu
        article.comment_count = Interaction.objects.filter(article=article, type='comment').count()

        get_article_related_details(
            request=request,
            article=article
        )

    # Przygotowanie kontekstu do przekazania do szablonu
    context = {
        'page_obj': page_obj,
    }

    # Renderowanie strony wykorzystując szablon 'main.html' i przygotowany kontekst
    return render(request, 'main.html', context)

def article_page(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    article.read_count += 1   # zwiększa liczbę wyświetleń przy każdej odsłonie
    article.save()

    get_article_related_details(
        request=request,
        article=article
    )

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


# Widok obsługujący aktywację śledzenia artykułu
# Tylko zalogowany użytkownik może śledzić artykuł
@login_required
def follow_article(request, article_id):
    requester = 'main'
    requester_url = '/'
    if request.method == "POST":
        requester = request.POST.get("requester")
        requester_url = request.POST.get('requester_url') or '/'

    # Pobierz artykuł, który użytkownik chce śledzić
    article = get_object_or_404(Article, pk=article_id)

    # Sprawdź, czy użytkownik już śledzi ten artykuł
    already_followed = ArticleWatch.objects.filter(
        user=request.user,
        article=article
    ).exists()

    # Jeśli nie śledzi to utworzymy nowy wpis
    if not already_followed:
        ArticleWatch.objects.create(
            user=request.user,
            article=article
        )

    if requester == 'main':
        # Po usunięciu śledzenia artykułu przekierowujemy użytkownika z powrotem na konkretną stronę
        # gdzie znajdował się nagłówek artykułu
        return redirect(requester_url)

        # Po usunięciu śledzenia artykułu przekierowujemy użytkownika z powrotem na stronę całego artykułu
    return redirect('article', article_id=article_id)


# Widok obsługujący dezaktywację śledzenia artykułu
@login_required
def unfollow_article(request, article_id):
    requester = 'main'
    requester_url = '/'
    if request.method == "POST":
        requester = request.POST.get("requester")
        requester_url = request.POST.get('requester_url') or '/'

    article = get_object_or_404(Article, pk=article_id)

    # Znajdź wystąpienie śledzenia dla tego użytkownika i artykułu
    followed = ArticleWatch.objects.filter(
        user=request.user,
        article=article
    ).first()

    # Usuń wystąpienie jeśli istnieje wystąpienie śledzenia dla tego użytkownika i artykułu
    if followed:
        followed.delete()

    if requester == 'main':
        # Po usunięciu śledzenia artykułu przekierowujemy użytkownika z powrotem na konkretną stronę
        # gdzie znajdował się nagłówek artykułu
        return redirect(requester_url)

        # Po usunięciu śledzenia artykułu przekierowujemy użytkownika z powrotem na stronę całego artykułu
    return redirect('article', article_id=article_id)


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

@login_required
def user_profile_view(request, user_id):  # Stworzenie funkcji user_profile_view, która przyjmuje user_id, znajduje użytkownika i renderuje stronę profilu
    user = get_object_or_404(User, id=user_id)

    # Zabezpieczenie, żeby nie oglądać swojego profilu w tym widoku
    if user == request.user:
        return redirect('profile_detail')

    # Szuka profilu powiązanego z użytkownikiem lub zwraca None, jeśli nie istnieje
    try:
        profile = UserProfile.objects.filter(user=user).first()
    except UserProfile.DoesNotExist:
        profile = None


    friendship = FriendshipModel.objects.filter(
        Q(user=request.user, friend=user) | Q(user=user, friend=request.user)
    ).first()

    context = {
        'profile_user': user,
        'profile': profile,
        'friendship_status': friendship.status if friendship else None,
    }

    return render(request, 'user_profile.html', context)

@login_required
def send_friend_request(request, user_id):
    friend = get_object_or_404(User, id=user_id)

    # Sprawdzenie czy nie wysyłamy zaproszenia do samego siebie
    if friend == request.user:
        messages.error(request, "Nie możesz wysłać zaproszenia do samego siebie.")
        return redirect('user_profile_view', user_id=friend.id)

    friendship = FriendshipModel.objects.filter(user=request.user, friend=friend).first()

    if friendship:
        if friendship.status == 'declined':
            friendship.status = 'pending'
            friendship.save()
            messages.success(request, f"Wysłano ponownie zaproszenie do {friend.username}")
        else:
            messages.info(request, f"Zaproszenie do {friend.username} już istnieje")
    else:
        FriendshipModel.objects.create(user=request.user, friend=friend, status='pending')
        messages.success(request, f"Wysłano zaproszenie do {friend.username}")

    return redirect('friends_list')


@login_required
def accept_friend_request(request, request_id):
    friendship = get_object_or_404(
        FriendshipModel,
        id=request_id,
        friend=request.user,
        status__in=['pending', 'declined']
    )
    friendship.status = 'accepted'
    friendship.save()
    messages.success(request, f"Zaakceptowano zaproszenie od {friendship.user.username}")
    return redirect('friends_list')


@login_required
def decline_friend_request(request, request_id):
    friendship = get_object_or_404(
        FriendshipModel,
        id=request_id,
        friend=request.user,
        status='pending'
    )
    friendship.status = 'declined'
    friendship.save()
    messages.info(request, f"Odrzucono zaproszenie od {friendship.user.username}")
    return redirect('friends_list')

@login_required
def friends_list_view(request):
    current_user = request.user

    # Znajomi (przykładowo)
    friends = current_user.friends.all()  # lub inny sposób, jeśli masz model relacji

    # Sugerowani użytkownicy — np. wszyscy poza sobą i aktualnymi znajomymi
    suggested_users = User.objects.exclude(id__in=friends).exclude(id=current_user.id)

    # Dodaj info, czy już jest oczekujące zaproszenie
    pending_requests = FriendshipModel.objects.filter(from_user=current_user, status='pending')
    pending_user_ids = set(pending_requests.values_list('to_user_id', flat=True))

    for user in suggested_users:
        user.pending_request = user.id in pending_user_ids

    return render(request, 'friends_list.html', {
        'friends': friends,
        'suggested_users': suggested_users,
    })
@login_required
def friends_list(request):
    # Pobranie zaakceptowanych znajomych
    friends = User.objects.filter(
        Q(friend_requests_received__user=request.user, friend_requests_received__status='accepted') |
        Q(friend_requests_sent__friend=request.user, friend_requests_sent__status='accepted')
    ).distinct()

    # Pobranie oczekujących zaproszeń dla zalogowanego użytkownika (jako odbiorca)
    pending_requests = FriendshipModel.objects.filter(friend=request.user, status='pending')
    pending_requests_count = pending_requests.count()

    # Pobranie użytkowników z relacją pending (wysłane lub otrzymane zaproszenia)
    all_pending_requests = FriendshipModel.objects.filter(
        Q(user=request.user, status='pending') | Q(friend=request.user, status='pending')
    )

    # Tworzenie listy użytkowników z oczekującymi zaproszeniami (wysłane lub otrzymane)
    pending_users_with_requests = []
    for friendship in all_pending_requests:
        if friendship.user == request.user:  # Zalogowany użytkownik wysłał zaproszenie
            user = friendship.friend
            sent_by_current_user = True
        else:  # Zalogowany użytkownik otrzymał zaproszenie
            user = friendship.user
            sent_by_current_user = False
        pending_users_with_requests.append({
            'user': user,
            'request_exists': True,
            'sent_by_current_user': sent_by_current_user,
            'request_id': friendship.id,
        })

    # Usunięcie duplikatów z listy pending
    seen_user_ids = set()
    unique_pending_users = []
    for item in pending_users_with_requests:
        if item['user'].id not in seen_user_ids:
            seen_user_ids.add(item['user'].id)
            unique_pending_users.append(item)
    pending_users_with_requests = unique_pending_users[:10]

    # Pobranie użytkowników bez żadnych relacji (ani pending, ani accepted)
    all_related_ids = set()
    all_related_ids.update(friend.id for friend in friends)
    pending_sent_ids = FriendshipModel.objects.filter(user=request.user, status='pending').values_list('friend_id', flat=True)
    pending_received_ids = FriendshipModel.objects.filter(friend=request.user, status='pending').values_list('user_id', flat=True)
    all_related_ids.update(pending_sent_ids)
    all_related_ids.update(pending_received_ids)
    all_related_ids.add(request.user.id)

    # Pobranie sugerowanych użytkowników (bez żadnych relacji)
    suggested_users = User.objects.exclude(id__in=all_related_ids)[:10]

    # Tworzenie listy sugerowanych użytkowników
    suggested_users_with_requests = []
    for user in suggested_users:
        suggested_users_with_requests.append({
            'user': user,
            'request_exists': False,
        })

    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'pending_users_with_requests': pending_users_with_requests,
        'suggested_users_with_requests': suggested_users_with_requests,
        'pending_requests_count': pending_requests_count,
    }
    return render(request, 'friends_list.html', context)

@login_required
def followed_articles(request):
    followed_interactions = Interaction.objects.filter(user=request.user, type='like')
    followed_articles = Article.objects.filter(id__in=followed_interactions.values('article_id'))

    # Annotate articles with liked_by_user status
    articles_with_status = []
    for article in followed_articles:
        article.liked_by_user = followed_interactions.filter(article=article).exists()
        articles_with_status.append(article)

    paginator = Paginator(articles_with_status, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Obserwowane artykuły',
    }
    return render(request, 'followed_articles.html', context)

@login_required
def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__username__icontains=query)
        )
    return render(request, 'search_results.html', {'results': results, 'query': query})
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
