#!/usr/bin/env python3
# encoding: utf-8


from entities.pymdbodm import CuestionExamen, Udfile, Udfuente, Udfuentecoor
from bson.objectid import ObjectId
from analyx.GenerarExamen import Generador
from random import randint



def generarExamen(generador, correccion):
    # Seleccionamos ficheros de nuestra practica. Luego de las de otros.
    fl_aut = Udfile.objects.raw({'$and': [
        {'tipo': Udfile.TIPO_SRC},
        {'lenguaje': 'python'},
        {'correccion': {'$eq': correccion.pk}}]})
    # TODO esto selecciona ficheros de otras correcciones si hubiera, cambiar.
    fl_oth = Udfile.objects.raw({'$and': [
        {'tipo': Udfile.TIPO_SRC},
        {'lenguaje': 'python'},
        {'correccion': {'$ne': correccion.pk}}]})
    
    # INVOCAMOS AL GENERADOR QUE NOS HAN PASADO PARA QUE REGENERE LAS AUTORIAS
    generador.generarautorias(fl_aut, fl_oth)
    preguntas = generador.get_peguntas()
    #print(len(preguntas), 'preguntas generadas')
    # Se guardan las preguntas para esa corrección.
    for bd_pr in preguntas:
        bd_pr.correccion = correccion.pk
        bd_pr.save()

