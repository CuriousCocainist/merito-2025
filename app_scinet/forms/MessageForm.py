from django import forms

class MessageForm(forms.ModelForm):
    text = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Napisz wiadomość...',
            'class': 'flex-grow border rounded-l px-4 py-2 focus:outline-none'
        })
    )

    class Meta:
        model = Message
        fields = ['text']
