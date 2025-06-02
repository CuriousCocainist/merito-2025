# Importujemy moduł do tworzenia własnych tagów szablonów Django
from django import template

# Importujemy model Message, który reprezentuje wiadomości w systemie czatu
from app_scinet.models.MessageModel import Message

# Rejestrujemy nową bibliotekę tagów (obiekt 'register' pozwala definiować niestandardowe tagi)
register = template.Library()

# Definiujemy niestandardowy tag szablonu typu "inclusion tag"
# Będzie on renderował określony fragment HTML (chat/unread_nav_icon.html)
# 'takes_context=True' oznacza, że do funkcji zostanie przekazany cały kontekst szablonu (np. request)


@register.inclusion_tag('chat/unread_nav_icon.html', takes_context=True)
def show_unread_messages_icon(context):
    # Pobieramy bieżącego użytkownika z kontekstu szablonu
    user = context['request'].user

    # Domyślna liczba nieprzeczytanych wiadomości to 0
    unread_count = 0

    # Jeśli użytkownik jest zalogowany
    if user.is_authenticated:
        # Zliczamy wszystkie wiadomości, które:
        # - należą do rozmowy, w której uczestniczy użytkownik
        # - są oznaczone jako nieprzeczytane (read=False)
        # - NIE zostały wysłane przez tego użytkownika (czyli są od innych)
        unread_count = Message.objects.filter(
            conversation__participants=user,
            read=False
        ).exclude(sender=user).count()

    # Zwracamy dane do użycia w szablonie chat/unread_nav_icon.html
    return {'unread_count': unread_count}
