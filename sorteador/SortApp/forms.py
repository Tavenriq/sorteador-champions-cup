from django import forms
from .models import Jogador, Time, Gol, Jogo

class JogadorForm(forms.ModelForm):
    class Meta:
        model = Jogador
        fields = ['nome', 'classificacao', 'overall', 'time']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'classificacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'overall': forms.NumberInput(attrs={'class': 'form-control'}),
            'time': forms.Select(attrs={'class': 'form-select'}),
        }

class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ['nome', 'escudo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'escudo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }