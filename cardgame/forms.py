from django import forms
from .models import Deck, CardDeck, Card

class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['name']

class CardDeckForm(forms.ModelForm):
    class Meta:
        model = CardDeck
        fields = ['card', 'quantity']

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['name', 'cost']