# forms.py
from django import forms
from .models import Transaction, Transfert

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['operateur', 'montant_total', 'bonus_total', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class TransfertForm(forms.ModelForm):
    class Meta:
        model = Transfert
        fields = ['employeur_source', 'employeur_cible', 'operateur', 'montant']
        # Exclure le champ 'date' car il est auto-généré
        exclude = ['date']
