#!/usr/bin/env python3
# encoding: utf-8



# Añadimos el path de MISTURE de modo que sean visibles los paquetes
import sys
#sys.path.append('/home/chilli-mint/Dropbox/MiStuRe/misture_core/MISTURE')


from entities.pymdbodm import *
from bson.objectid import ObjectId
from analyx.CodeAnaly import PylintAn, PylintError




def analisis_errores(ruta, correccion, codigos_exc= 'E125,E127,E128'):
    # obtener los udfiles de cada correcion del tipo python
    # listar su relpath y la ruta base del repo.
    errores = []
    try:
        files=Udfile.objects.raw({'tipo': Udfile.TIPO_SRC, 'lenguaje': 'python',
                                  'correccion': correccion.pk})
        names = [x['pathrel'] for x in files.only('pathrel').values()]
        
        res = PylintAn.analy_pylint_msgs(ruta, names, codigos_exc)
     
        
        for i,er in enumerate(res):
            error = CodeError(correccion=correccion.pk, fichero=er.path,
                              fila=er.line, columna=er.column,
                              tipo=er.type, descripcion=er.message[:200])
            error.save(cascade=False)
            errores.append(error)
            #print(i, er.path)
        return errores
    except:
        # TODO MANEJAR, LOGERROR.
        raise
    
    
