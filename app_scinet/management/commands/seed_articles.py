from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from app_scinet.models import Article


class Command(BaseCommand):
    help = "Czyści tabelę Article i tworzy przykładowe artykuły"

    def handle(self, *args, **kwargs):
        Article.objects.all().delete()
        self.stdout.write(self.style.WARNING("Wyczyszczono tabelę Article."))

        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("Nie znaleziono użytkownika."))
            return
        articles = [
            {
                "title": "Tytuł artykułu 1",
                "content": "Przykładowy artykuł o sztucznej inteligencji i jej zastosowaniach w różnych dziedzinach..."
                           "Przykładowy artykuł o sztucznej inteligencji i jej zastosowaniach w różnych dziedzinach..."
                           "Przykładowy artykuł o sztucznej inteligencji i jej zastosowaniach w różnych dziedzinach..."
                           "Przykładowy artykuł o sztucznej inteligencji i jej zastosowaniach w różnych dziedzinach...",
                "user": user
            },
            {
                "title": "Tytuł artykułu 2",
                "content": "Jakiś tekst o nauce i technologii, który może być interesujący dla czytelników..."
                           "Jakiś tekst o nauce i technologii, który może być interesujący dla czytelników..."
                           "Jakiś tekst o nauce i technologii, który może być interesujący dla czytelników...",
                "user": user

            },
            {
                "title": "Tytuł artykułu 3",
                "content": "Nie mam pomysłu na treść, ale to jest przykładowy artykuł o czymś ważnym... i może być ciekawy. i jeszcze coś..."
                           "Nie mam pomysłu na treść, ale to jest przykładowy artykuł o czymś ważnym... i może być ciekawy. i jeszcze coś..."
                           "Nie mam pomysłu na treść, ale to jest przykładowy artykuł o czymś ważnym... i może być ciekawy. i jeszcze coś..."
                           "Nie mam pomysłu na treść, ale to jest przykładowy artykuł o czymś ważnym... i może być ciekawy. i jeszcze coś...",
                "user": user
            },
            {
                "title": "Jimi Hendrix - art no. 4",
                "content": "James Marshall \"Jimi\" Hendrix (born Johnny Allen Hendrix; November 27, 1942 – September 18, 1970) was an American guitarist, songwriter and singer"
                           "He is widely regarded as one of the greatest and most influential guitarists of all time."
                           "Inducted into the Rock and Roll Hall of Fame in 1992 as a part of his band, the Jimi Hendrix Experience, the institution describes him as \"arguably the greatest instrumentalist in the history of rock music.\"",
                "user": user
            },
            {
                "title": "Bruce Lee - art no. 5",
                "content": "Bruce Lee (born Lee Jun-fan; November 27, 1940 – July 20, 1973) was a Hong Kong-American martial artist, actor, filmmaker, and philosopher."
                           "He was the founder of Jeet Kune Do, a hybrid martial arts philosophy which was formed from Lee's experiences in unarmed fighting and self-defense—as well as eclectic, Zen Buddhist and Taoist philosophies—as a new school of martial arts thought"
                           "With a film career spanning Hong Kong and the United States, Lee is regarded as the first global Chinese film star and one of the most influential martial artists in the history of cinema."
                           "Known for his roles in five feature-length martial arts films, Lee is credited with helping to popularize martial arts films in the 1970s and promoting Hong Kong action cinema.",
                "user": user
            },
            {
                "title": "Koziołek Matołek - art no. 6",
                "content": "Koziołek Matołek is a beloved literary character created by Kornel Makuszyński, a Polish writer"
                           "Matołek is known for his adventurous spirit and clever solutions to problems he encounters on his travels. "
                           "Koziołek Matołek has been charming readers of all ages for generations :) ",
                "user": user
            }
        ]

        for article in articles:
            Article.objects.create(
                title=article["title"],
                content=article["content"],
                user=article["user"]
            )

        self.stdout.write(self.style.SUCCESS("Dodano przykładowe artykuły"))
