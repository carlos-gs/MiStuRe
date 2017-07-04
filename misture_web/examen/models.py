from django.db import models

# Create your models here.

from django.core.exceptions import ValidationError


def valida_cantidad(value): # Ver validacion model y forms
    if value < 1 or value > 50:
        raise ValidationError(u'Valor debe %s estar entre 1-50' % value)

