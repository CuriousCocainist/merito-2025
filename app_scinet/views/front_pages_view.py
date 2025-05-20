from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
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


def get_article_related_details(request, article):
    if request.user.is_authenticated:
        # Tworzymy nowy atrybut `liked_by_user` w artykule
        # Sprawdzamy, czy istnieje w bazie wpis interakcji typu 'like'
        # przypisany do tego artykułu i tego użytkownika
        article.liked_by_user = Interaction.objects.filter(
            article=article,
            user=request.user,
            type='like'
        ).exists()

        # Tworzymy nowy atrybut `followed_by_user` w artykule
        # Sprawdzamy, czy istnieje w bazie wpis
        # przypisany do tego artykułu i tego użytkownika
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
    articles = Article.objects.all().order_by('-created_at')

    # Przechodzimy przez wszystkie artykuły pobrane wcześniej z bazy danych
    for article in articles:

        # Tworzymy nowy atrybut `like_count` w obiekcie `article`
        # Wartość to liczba interakcji typu 'like' związanych z tym artykułem
        article.like_count = Interaction.objects.filter(article=article, type='like').count()

        # Tworzymy nowy atrybut `comment_count` w obiekcie `article`
        # Wartość to liczba interakcji typu 'comment' dla tego artykułu
        article.comment_count = Interaction.objects.filter(article=article, type='comment').count()

        get_article_related_details(
            request=request,
            article=article
        )

    # Tworzymy słownik `context`, który przekażemy do szablonu
    # Zawiera on listę artykułów z dodatkowymi atrybutami (lajki, komentarze, polubienia użytkownika)
    context = {
        'articles': articles
    }

    return render(request, 'main.html', context)


def article_page(request, article_id):
    article = get_object_or_404(Article, id=article_id)

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
@login_required  # Tylko zalogowany użytkownik może śledzić artykuł
def follow_article(request, article_id):
    requester = 'main'
    if request.method == "POST":
        requester = request.POST.get("requester")

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
        # Po dodaniu śledzenia artykułu przekierowujemy użytkownika z powrotem na stronę główną
        return redirect('home')
    # Po dodaniu śledzenia artykułu przekierowujemy użytkownika z powrotem na stronę artykułu
    return redirect('article', article_id=article_id)


# Widok obsługujący dezaktywację śledzenia artykułu
@login_required
def unfollow_article(request, article_id):
    requester = 'main'
    if request.method == "POST":
        requester = request.POST.get("requester")

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
        # Po usunięciu śledzenia artykułu przekierowujemy użytkownika z powrotem na stronę główną
        return redirect('home')
    # Po usunięciu śledzenia artykułu przekierowujemy użytkownika z powrotem na stronę artykułu
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
def user_profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Zabezpieczenie, żeby nie oglądać swojego profilu w tym widoku
    if user == request.user:
        return redirect('profile')

    profile = get_object_or_404(UserProfile, user=user)

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

    # Sprawdzenie czy zaproszenie już istnieje
    friendship, created = FriendshipModel.objects.get_or_create(
        user=request.user,
        friend=friend,
        defaults={'status': 'pending'}
    )

    if created:
        messages.success(request, f"Wysłano zaproszenie do {friend.username}")
    else:
        messages.info(request, f"Zaproszenie do {friend.username} już istnieje")

    return redirect('user_profile_view', user_id=friend.id)


@login_required
def accept_friend_request(request, request_id):
    friendship = get_object_or_404(
        FriendshipModel,
        id=request_id,
        friend=request.user,
        status='pending'
    )
    friendship.status = 'accepted'
    friendship.save()
    messages.success(request, f"Zaakceptowano zaproszenie od {friendship.user.username}")
    return redirect('user_profile_view', user_id=friendship.user.id)


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
    return redirect('user_profile_view', user_id=friendship.user.id)


@login_required
def friends_list(request):
    # Pobranie zaakceptowanych znajomych
    friends = User.objects.filter(
        Q(friend_requests_received__user=request.user,
          friend_requests_received__status='accepted') |
        Q(friend_requests_sent__friend=request.user,
          friend_requests_sent__status='accepted')
    ).distinct()

    # Pobranie sugerowanych użytkowników (wszyscy użytkownicy oprócz znajomych i obecnego użytkownika)
    suggested_users = User.objects.exclude(
        id__in=[friend.id for friend in friends]
    ).exclude(
        id=request.user.id
    )[:5]  # limitujemy do 5 sugestii

    context = {
        'friends': friends,
        'suggested_users': suggested_users,
    }

    return render(request, 'friends_list.html', context)