#!/usr/bin/env python3
# encoding: utf-8


import ast
import astor
import linecache
import json
import os.path as op
from random import randint

from bson.objectid import ObjectId

import pymodm
from pymodm.queryset import QuerySet

from entities.pymdbodm import CuestionExamen, Udfile, Udfuente, Udfuentecoor, \
    LogError
import random

# CONSTANTES SOBRE EL TIPO DE PREGUNTA
PR_TIPO_ABIERTA = 'abierta'
PR_TIPO_OPCIONES = 'opciones'
PR_TIPO_TEXTO = 'texto'
PR_TIPOS = (PR_TIPO_ABIERTA, PR_TIPO_OPCIONES, PR_TIPO_TEXTO)

class Generador:
    
    MAX_AUTORIAS = 6
    MAX_NO_AUTORIAS = 4
    
    def __init__(self, ruta_json, fichero_json='examen.json'):
        try:
            self.preguntas_autor = None
            self.preguntas_json = self.__leerjson(ruta_json, fichero_json)
            self.preguntas_autor = []
            self.ruta_json = ruta_json
            self.fichero_json = fichero_json
            self.autoria = ''  # Para el id de la autoria.
        except:
            raise
     
    def generarautorias(self, qpropias=None, qajenas=None):
        '''
        Dadas una querie de Udfuente con ficheros propios y otra con no propios,
        asigna pseudoaleatoriamente preguntas de autoria basandose en snippeds
        de código de clases o funciones. Se almacenan en self.preguntas_autor
        :param qpropias: QuerySet de entities.pymodmbd.Udfuente
        :param qajenas: QuerySet de entities.pymodmbd.Udfuente
        :return: None.
        '''
        if not (isinstance(qpropias, pymodm.queryset.QuerySet) and
                    isinstance(qajenas, pymodm.queryset.QuerySet)):
            raise Exception('generarautorias, se espera Udfuente como pars')
        
        
        # Filtramos las que son codigo python, extraemos sus pathrel del repo.
        src_prop = qpropias.raw({'tipo': Udfile.TIPO_SRC, 'lenguaje': 'python'})
        fich_prop = set([x['pathrel'] for x in src_prop.only('pathrel').values()])
        
        src_no = qajenas.raw({'tipo': Udfile.TIPO_SRC, 'lenguaje': 'python'})
        fich_np = set([x['pathrel'] for x in src_no.only('pathrel').values()])
        #print('QUERIES ', src_prop.count(), src_no.count())
        fich_todas = fich_prop.union(fich_np)
        
        # TODO NOS FALTARIA PODER FILTRAR ALGUNOS NOMBRES DE FICHEROS o FUNCIONES
        # QUE YA SABEMOS O NOS PASAN COMO PARAMETRO QUE NO QUEREMOS.
        # ESTA EXCLUSION PROB. NO SE PUEDA HACER CON QUERIES MONGO.
        
        propias = []
        for sp in src_prop:
            sp_srcs = Udfuente.objects.raw({'$and': [
                {'snipped': {'$exists': True}}, {'udfile': sp.pk}]})
            # print(sp_srcs.count(), sp.nombre)
            for i,x in enumerate(sp_srcs):
                # print('#', i,x.pk,x.nombre, type(sp_srcs))
                propias.append((sp.pathrel, x))
        
        nopropias = []
        for sn in src_no:
            sn_srcs = Udfuente.objects.raw({'$and': [
                {'snipped': {'$exists': True}}, {'udfile': sn.pk}]})
            # print(sn_srcs.count(), sn.nombre)
            for i, x in enumerate(sn_srcs):
                # print('#', i, x.pk,x.nombre, type(sn_srcs))
                nopropias.append((sn.pathrel, x))
        
        npr = len(propias)
        nnp = len(nopropias)
        prop_rnd = set([randint(0, max(npr-1, 0)) for x in range(self.MAX_AUTORIAS)])
        np_rnd = set([randint(0, max(nnp-1, 0)) for x in range(self.MAX_NO_AUTORIAS)])
        
        # print(prop_rnd, np_rnd)
        
        # Generamos las cuestiones a partir de los udfuente propias/nopropias
        preguntas = []
        for num in prop_rnd:
            if not npr:
                break
            pr = propias[num]
            resto = fich_todas.copy()
            resto.discard(pr[0])
            posibles=['No', 'Si, ' + pr[0]] + \
                    ['Si, ' + x for x in list(resto)[:
                    min(3, max(0, len(fich_prop) - 1))]]
            random.shuffle(posibles)
            
            cues = CuestionExamen(#correccion= esto se hace en func..examen
                tipo=CuestionExamen.TIPO_OPCIONES,
                opciones_validas=['Si, ' + pr[0]],
                contenido='<pre> {} </pre> \n'.format(pr[1].snipped),
                pregunta='\n¿Es tuyo este código?\n',
                opciones_respuesta=posibles
            )
            preguntas.append(cues)
        for num in np_rnd:
            if not nnp:
                break
            pr = nopropias[num]
            resto = fich_todas.copy()
            resto.discard(pr[0])
            posibles=['No', 'Si ' + pr[0]] + \
                           ['Si, ' + x for x in list(resto)[:
                           min(3, max(0, len(fich_np) - 1))]]
            random.shuffle(posibles)
            cues = CuestionExamen(#correccion= esto se hace en func..examen
                tipo=CuestionExamen.TIPO_OPCIONES,
                opciones_validas=['No'],
                pregunta='\n¿Es tuyo este código?\n',
                contenido='<pre> {} </pre> \n\n¿Es tuyo este código?\n'.format(pr[1].snipped),
                opciones_respuesta=posibles
            )
            preguntas.append(cues)
        
        # Substituyo las preguntas de autoria
        self.preguntas_autor = preguntas
        
        
    def get_peguntas(self):
        return self.preguntas_json.copy() + self.preguntas_autor.copy()
       

    def __leerjson(self, rutabase, fichero_json='examen.json'):
        cuestiones_leidas = []
        # Lectura del JSON de examen
        jexamen = op.normpath(op.join(rutabase, fichero_json))
        if not op.exists(jexamen):
            raise Exception('Error leyendo el examen desde {}'.format(jexamen))
        try:
            with open(jexamen) as fp:
                j = json.load(fp)
            # VALIDAMOS LA LÓGICA DE LAS CUESTIONES LEIDAS Y ALMACENAMOS
            for np, ct in enumerate(j['examen']):
                ct_bd = CuestionExamen()
                if not ('tipo' in ct or 'pregunta' in ct):
                    raise Exception('Error: la pregunta leida en ' + ' np' +
                                    ' lugar debe contener tipo y pregunta')
                tipo = ct['tipo']
                
                if tipo == 'abierta':
                    ct_bd.tipo = CuestionExamen.TIPO_ABIERTA
                elif tipo == 'opciones':
                    if not ('opciones_respuesta' in ct or 'opciones_validas' in ct):
                        raise Exception('Error: pregunta tipo {} debe tener '
                            'opciones_validas y opciones_respuesta'.format(tipo))
                    ct_bd.tipo = CuestionExamen.TIPO_OPCIONES
                    ct_bd.opciones_validas = ct['opciones_validas']
                    ct_bd.opciones_respuesta = ct['opciones_respuesta']
                
                elif tipo == 'texto':
                    if not ('opciones_validas' in ct):
                        raise Exception('Error: pregunta tipo {} debe tener '
                            'opciones_validas, sino, es abierta.'.format(tipo))
                    ct_bd.tipo = CuestionExamen.TIPO_TEXTO
                    ct_bd.opciones_validas = ct['opciones_validas']
                else:
                    raise Exception('Error: tipo {} debe pertenecer a {}'.format(
                        tipo, PR_TIPOS))
                
                if 'contenido' in ct:
                    fcont = op.normpath(op.join(rutabase, ct['contenido']))
                    if not op.exists(jexamen):
                        raise Exception('No existe contenido en ' + fcont)
                    with open(fcont) as fp:
                        lines = fp.readlines()
                    contenido = ''.join(lines)
                    ct_bd.contenido = contenido
                else:
                    contenido = 'Contexta a lo siguiente:'
                
                ct_bd.pregunta = ct['pregunta']
                cuestiones_leidas.append(ct_bd)
            
            return cuestiones_leidas
            
        except Exception as jde:
            LogError(descripcion='GenerarExamen.Generador.__leerjson ' +
                     str(jde) + ' para ruta ' + jexamen)
            raise



 
        
    
    
    
    