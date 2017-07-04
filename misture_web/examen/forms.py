#!/usr/bin/env python3
# encoding: utf-8

from django import forms
from .models import valida_cantidad


class CuestionExamenForm(forms.Form):
    # TODO LIMPIAR ESTE FORMULARIO CON LOS CAMPOS REALMENTE USADOS
    siguiente = forms.CharField(max_length=100, widget=forms.HiddenInput())
    revistausuario = forms.CharField(max_length=100, widget=forms.HiddenInput())
    FAVORITE_COLORS_CHOICES = tuple(
        (str(i), 'OPCION ' + str(i)) for i in range(1, 6))
    numeronoticias = forms.IntegerField(validators=[valida_cantidad])
    color = forms.ChoiceField(choices=FAVORITE_COLORS_CHOICES,
                              widget=forms.RadioSelect)
    texto = forms.CharField(max_length=100)


class ConfirmarForm(forms.Form):
    idcorreccion = forms.CharField(max_length=100,widget=forms.HiddenInput())
