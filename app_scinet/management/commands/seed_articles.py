import random
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from app_scinet.models import Article


class Command(BaseCommand):
    help = "Czyści tabelę Article i tworzy przykładowe artykuły"

    def handle(self, *args, **kwargs):
        Article.objects.all().delete()
        self.stdout.write(self.style.WARNING("Wyczyszczono tabelę Article."))

        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR("Brak użytkowników w bazie danych."))
            return

        articles = [
            {
                "title": "Wprowadzenie do języka Python dla początkujących",
                "content": "Python to wszechstronny język programowania znany z czytelnej składni. "
                           "Ten artykuł omawia podstawowe elementy: zmienne, typy danych, operatory i instrukcje warunkowe."
            },
            {
                "title": "Pętle i funkcje w Pythonie – jak pisać czytelny kod",
                "content": "Dowiedz się, jak używać pętli `for`, `while`, oraz jak definiować i wywoływać funkcje. "
                           "Zrozumiesz także pojęcie zakresu zmiennych i przekazywania argumentów."},
            {
                "title": "Struktury danych w Pythonie – listy, słowniki i zbiory",
                "content": "Artykuł omawia kluczowe struktury danych: jak je tworzyć, modyfikować oraz stosować w praktycznych przypadkach, takich jak filtrowanie danych."},
            {
                "title": "Obsługa błędów w Pythonie – try, except, finally",
                "content": "W tym artykule uczysz się, jak radzić sobie z wyjątkami w Pythonie. Pokazujemy najlepsze praktyki stosowania `try`, `except`, `else` i `finally`."},
            {
                "title": "Praca z plikami w Pythonie – wczytywanie i zapisywanie danych",
                "content": "Dowiesz się, jak otwierać pliki tekstowe, czytać dane linia po linii oraz zapisywać wyniki do nowych plików przy użyciu `with open()`."},
            {
                "title": "Moduły i pakiety w Pythonie – jak organizować projekt",
                "content": "Artykuł wyjaśnia, jak importować moduły standardowe i własne, oraz jak tworzyć własne pakiety w celu lepszej organizacji kodu."},
            {
                "title": "Zrozumienie list comprehensions w Pythonie",
                "content": "List comprehensions pozwalają tworzyć listy w jednej linijce kodu. Artykuł zawiera praktyczne przykłady oraz porównania z klasycznymi pętlami."},
            {
                "title": "Wprowadzenie do programowania obiektowego w Pythonie",
                "content": "Dowiesz się, czym są klasy, obiekty, dziedziczenie i enkapsulacja. Poznasz praktyczne przykłady projektowania klas."},
            {
                "title": "Instalacja i użycie bibliotek z pip – podstawy pracy z zależnościami",
                "content": "Opisujemy jak zainstalować biblioteki takie jak `requests`, `numpy`, czy `matplotlib`, oraz jak zarządzać środowiskami przy użyciu `venv`."},
            {
                "title": "Testowanie kodu w Pythonie z unittest i pytest",
                "content": "Testy jednostkowe pozwalają wykrywać błędy wcześniej. Artykuł pokazuje, jak pisać testy w `unittest` oraz `pytest`, z przykładami."},
            {
                "title": "Czym jest sztuczna inteligencja – podstawowe pojęcia",
                "content": "AI to dziedzina informatyki zajmująca się tworzeniem systemów naśladujących ludzką inteligencję. Poznasz różnicę między AI, ML i deep learningiem."},
            {
                "title": "Uczenie maszynowe w praktyce – typy i zastosowania",
                "content": "Omawiamy uczenie nadzorowane i nienadzorowane, regresję, klasyfikację oraz realne zastosowania AI w biznesie, medycynie i finansach."},
            {
                "title": "Biblioteka scikit-learn – pierwsze modele ML w Pythonie",
                "content": "Zobacz, jak zbudować swój pierwszy model klasyfikacyjny przy użyciu scikit-learn: od przygotowania danych po ocenę jakości modelu."},
            {
                "title": "Sztuczne sieci neuronowe – jak działa perceptron",
                "content": "W artykule omawiamy budowę i działanie perceptronu – podstawowego elementu sieci neuronowych. Pojawia się także prosty kod implementacyjny."},
            {
                "title": "TensorFlow – jak zbudować prostą sieć neuronową",
                "content": "Dowiesz się, jak stworzyć prosty model sieci neuronowej w TensorFlow – od definicji warstw po trening i ewaluację."},
            {
                "title": "Uczenie głębokie z Keras – klasyfikacja obrazów",
                "content": "W artykule używamy Keras do stworzenia klasyfikatora obrazów. Omówione są konwolucyjne sieci neuronowe i preprocessing danych."},
            {
                "title": "Naturalne przetwarzanie języka – NLP z biblioteką spaCy",
                "content": "Przetwarzanie języka naturalnego pozwala analizować tekst, rozpoznawać encje i klasyfikować sentyment. Przykłady kodu z wykorzystaniem spaCy."},
            {
                "title": "Wstęp do chatbotów opartych na AI",
                "content": "Dowiedz się, jak działają chatboty, jak trenować je na bazie dialogów i używać narzędzi typu Rasa lub Dialogflow."},
            {
                "title": "Wykrywanie obiektów na obrazach – YOLO i inne algorytmy",
                "content": "Poznasz zasady działania algorytmów do wykrywania obiektów takich jak YOLO czy SSD oraz jak je zaimplementować z użyciem Python."},
            {
                "title": "AI w życiu codziennym – inteligentne systemy rekomendacyjne",
                "content": "Wyjaśniamy, jak działają rekomendacje na platformach takich jak Netflix czy Spotify i jak samodzielnie stworzyć prosty system rekomendacji."},
            {
                "title": "Wprowadzenie do języka Python dla początkujących",
                "content": "Python to wszechstronny język programowania znany z czytelnej składni. "
                           "Ten artykuł omawia podstawowe elementy: zmienne, typy danych, operatory i instrukcje warunkowe."},
            {
                "title": "Pętle i funkcje w Pythonie – jak pisać czytelny kod",
                "content": "Dowiedz się, jak używać pętli `for`, `while`, oraz jak definiować i wywoływać funkcje. "
                           "Zrozumiesz także pojęcie zakresu zmiennych i przekazywania argumentów."},
            {
                "title": "Struktury danych w Pythonie – listy, słowniki i zbiory",
                "content": "Artykuł omawia kluczowe struktury danych: jak je tworzyć, modyfikować oraz stosować w praktycznych przypadkach, takich jak filtrowanie danych."},
            {
                "title": "Obsługa błędów w Pythonie – try, except, finally",
                "content": "W tym artykule uczysz się, jak radzić sobie z wyjątkami w Pythonie. Pokazujemy najlepsze praktyki stosowania `try`, `except`, `else` i `finally`."},
            {
                "title": "Praca z plikami w Pythonie – wczytywanie i zapisywanie danych",
                "content": "Dowiesz się, jak otwierać pliki tekstowe, czytać dane linia po linii oraz zapisywać wyniki do nowych plików przy użyciu `with open()`."},
            {
                "title": "Moduły i pakiety w Pythonie – jak organizować projekt",
                "content": "Artykuł wyjaśnia, jak importować moduły standardowe i własne, oraz jak tworzyć własne pakiety w celu lepszej organizacji kodu."},
            {
                "title": "Zrozumienie list comprehensions w Pythonie",
                "content": "List comprehensions pozwalają tworzyć listy w jednej linijce kodu. Artykuł zawiera praktyczne przykłady oraz porównania z klasycznymi pętlami."},
            {
                "title": "Wprowadzenie do programowania obiektowego w Pythonie",
                "content": "Dowiesz się, czym są klasy, obiekty, dziedziczenie i enkapsulacja. Poznasz praktyczne przykłady projektowania klas."},
            {
                "title": "Instalacja i użycie bibliotek z pip – podstawy pracy z zależnościami",
                "content": "Opisujemy jak zainstalować biblioteki takie jak `requests`, `numpy`, czy `matplotlib`, oraz jak zarządzać środowiskami przy użyciu `venv`."},
            {
                "title": "Testowanie kodu w Pythonie z unittest i pytest",
                "content": "Testy jednostkowe pozwalają wykrywać błędy wcześniej. Artykuł pokazuje, jak pisać testy w `unittest` oraz `pytest`, z przykładami."},
            {
                "title": "Czym jest sztuczna inteligencja – podstawowe pojęcia",
                "content": "AI to dziedzina informatyki zajmująca się tworzeniem systemów naśladujących ludzką inteligencję. Poznasz różnicę między AI, ML i deep learningiem."},
            {
                "title": "Uczenie maszynowe w praktyce – typy i zastosowania",
                "content": "Omawiamy uczenie nadzorowane i nienadzorowane, regresję, klasyfikację oraz realne zastosowania AI w biznesie, medycynie i finansach."},
            {
                "title": "Biblioteka scikit-learn – pierwsze modele ML w Pythonie",
                "content": "Zobacz, jak zbudować swój pierwszy model klasyfikacyjny przy użyciu scikit-learn: od przygotowania danych po ocenę jakości modelu."},
            {
                "title": "Sztuczne sieci neuronowe – jak działa perceptron",
                "content": "W artykule omawiamy budowę i działanie perceptronu – podstawowego elementu sieci neuronowych. Pojawia się także prosty kod implementacyjny."},
            {
                "title": "TensorFlow – jak zbudować prostą sieć neuronową",
                "content": "Dowiesz się, jak stworzyć prosty model sieci neuronowej w TensorFlow – od definicji warstw po trening i ewaluację."},
            {
                "title": "Uczenie głębokie z Keras – klasyfikacja obrazów",
                "content": "W artykule używamy Keras do stworzenia klasyfikatora obrazów. Omówione są konwolucyjne sieci neuronowe i preprocessing danych."},
            {
                "title": "Naturalne przetwarzanie języka – NLP z biblioteką spaCy",
                "content": "Przetwarzanie języka naturalnego pozwala analizować tekst, rozpoznawać encje i klasyfikować sentyment. Przykłady kodu z wykorzystaniem spaCy."},
            {
                "title": "Wstęp do chatbotów opartych na AI",
                "content": "Dowiedz się, jak działają chatboty, jak trenować je na bazie dialogów i używać narzędzi typu Rasa lub Dialogflow."},
            {
                "title": "Wykrywanie obiektów na obrazach – YOLO i inne algorytmy",
                "content": "Poznasz zasady działania algorytmów do wykrywania obiektów takich jak YOLO czy SSD oraz jak je zaimplementować z użyciem Python."},
            {
                "title": "AI w życiu codziennym – inteligentne systemy rekomendacyjne",
                "content": "Wyjaśniamy, jak działają rekomendacje na platformach takich jak Netflix czy Spotify i jak samodzielnie stworzyć prosty system rekomendacji."}
        ]

        for article in articles:
            Article.objects.create(
                title=article["title"],
                content=article["content"],
                user = random.choice(users)
            )

        self.stdout.write(self.style.SUCCESS("Dodano przykładowe artykuły"))
