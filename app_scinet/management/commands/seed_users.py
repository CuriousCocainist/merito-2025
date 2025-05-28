from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from app_scinet.models.UserProfileModel import UserProfile


class Command(BaseCommand):
    help = "Czyści użytkowników (oprócz superuserów) i tworzy 10 testowych użytkowników z profilami + dodaje profile superuserom"

    def handle(self, *args, **kwargs):
        # Usuń użytkowników niebędących superuserami
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("🗑 Usunięto użytkowników niebędących superuserami."))

        # Dodaj profile dla istniejących superuserów
        superusers = User.objects.filter(is_superuser=True)
        for su in superusers:
            if not hasattr(su, 'profile'):
                UserProfile.objects.create(
                    user=su,
                    bio="Profil superużytkownika",
                    phone_number="000000000",
                    birth_date=None,
                    location="Nieznana lokalizacja"
                )
                self.stdout.write(self.style.SUCCESS(f"➕ Dodano profil dla superusera: {su.username}"))

        # Dodaj przykładowych użytkowników
        sample_users = [
            {"username": "jan.kowalski", "email": "jan.kowalski@example.com", "first_name": "Jan", "last_name": "Kowalski", "bio": "Entuzjasta technologii.", "phone": "123456789", "birth": "1990-01-01", "location": "Warszawa"},
            {"username": "anna.nowak", "email": "anna.nowak@example.com", "first_name": "Anna", "last_name": "Nowak", "bio": "Specjalistka ds. AI.", "phone": "987654321", "birth": "1988-03-15", "location": "Kraków"},
            {"username": "adam.kwiatkowski", "email": "adam.k@example.com", "first_name": "Adam", "last_name": "Kwiatkowski", "bio": "Front-end Developer.", "phone": "555111222", "birth": "1995-06-10", "location": "Gdańsk"},
            {"username": "ewa.zielinska", "email": "ewa.z@example.com", "first_name": "Ewa", "last_name": "Zielińska", "bio": "UX Designerka.", "phone": "666333444", "birth": "1992-09-23", "location": "Poznań"},
            {"username": "marek.nowicki", "email": "marek.n@example.com", "first_name": "Marek", "last_name": "Nowicki", "bio": "Data Scientist.", "phone": "444222111", "birth": "1985-12-05", "location": "Wrocław"},
            {"username": "kasia.adamska", "email": "kasia.a@example.com", "first_name": "Kasia", "last_name": "Adamska", "bio": "PM w startupie.", "phone": "321321321", "birth": "1991-07-17", "location": "Szczecin"},
            {"username": "tomasz.baran", "email": "t.baran@example.com", "first_name": "Tomasz", "last_name": "Baran", "bio": "Python Developer.", "phone": "888777666", "birth": "1993-05-09", "location": "Lublin"},
            {"username": "paula.maj", "email": "p.maj@example.com", "first_name": "Paula", "last_name": "Maj", "bio": "Specjalistka SEO.", "phone": "777888999", "birth": "1994-11-30", "location": "Katowice"},
            {"username": "lukasz.wozniak", "email": "lukasz.w@example.com", "first_name": "Łukasz", "last_name": "Woźniak", "bio": "Administrator IT.", "phone": "999000111", "birth": "1987-04-18", "location": "Łódź"},
            {"username": "martyna.olszewska", "email": "martyna.o@example.com", "first_name": "Martyna", "last_name": "Olszewska", "bio": "Marketing Managerka.", "phone": "123789456", "birth": "1996-02-25", "location": "Rzeszów"},
        ]

        for u in sample_users:
            user = User.objects.create_user(
                username=u["username"],
                email=u["email"],
                password="test1234",
                first_name=u["first_name"],
                last_name=u["last_name"]
            )
            UserProfile.objects.create(
                user=user,
                bio=u["bio"],
                phone_number=u["phone"],
                birth_date=u["birth"],
                location=u["location"]
            )

        self.stdout.write(self.style.SUCCESS("✅ Dodano 10 użytkowników oraz ich profile!"))
