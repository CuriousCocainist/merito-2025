# forms.py
from django import forms
from app_scinet.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'access_level', 'file', 'image']  # Pola dostępne w formularzu

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Specjalne style dla pól typu "file"
        self.fields['image'].widget.attrs.update({
            'accept': 'image/*',
            'class': 'block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500'
        })
        self.fields['file'].widget.attrs.update({
            'class': 'block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500'
        })
        # Styl dla pola 'access_level' (dropdown)
        self.fields['access_level'].widget.attrs.update({
            'class': 'block w-full text-sm border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'
        })

        # Style dla pozostałych pól
        for name, field in self.fields.items():
            if name not in ['file', 'image', 'access_level']:
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500'
                })

