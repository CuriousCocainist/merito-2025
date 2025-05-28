# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Article
import os

@login_required  # <-- usuń jeśli dostęp ma być publiczny
def download_article_file(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if not article.file:
        messages.error(request, "Brak pliku do pobrania.")
        return redirect('article', article_id=article.id)

    file_path = article.file.path

    if not os.path.exists(file_path):
        messages.error(request, "Plik nie istnieje.")
        return redirect('article', article_id=article.id)

    return FileResponse(open(file_path, 'rb'), as_attachment=True)