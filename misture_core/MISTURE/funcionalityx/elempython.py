#!/usr/bin/env python3
# encoding: utf-8




import os.path as op

from bson.objectid import ObjectId

'''
import sys
sys.path.append('/home/chilli-mint/Dropbox/MiStuRe/misture_core/MISTURE')
import pymodm
pymodm.connect('mongodb://localhost:27017/' + 'misture_mbbd')
'''
from entities.pymdbodm import Udfile, LogError, DirectoriosActividad

from analyx.PyGrammarAnaly import analy_pygrammar







def analisis_python(ruta, correccion):

    # OBTENER LOS FICHEROS DE ESE ALUMNO CONCRETO
    udfiles = Udfile.objects.raw(
        {'$and': [{'tipo': Udfile.TIPO_SRC}, {'lenguaje': 'python'},
                  {'correccion': correccion.pk}]})
      
    try:
        for ud in udfiles:  # for file in udfiles con codigo fuente
            # ruta = x.correccion.actividad.directorios.pentrega + ¿?
            rfich = DirectoriosActividad.unir(ruta, ud.pathrel)
            #print(op.exists(rfich), rfich, ud.correccion.pk)
            
            try:
                elementos = analy_pygrammar(rfich)
                #print(len(elementos), elementos)
            except Exception as e:
                # TODO FALTA ASIGNARLE ACTIVIDAD O CORRECCION
                LogError(descripcion='No se ha analizado {} en sus '
                                     'elementos python: {}'.format(rfich, str(
                    e))).save()
                raise
            
            # todo asignar los elementos de corr al fichero y guardar
            # for x in elementos: x.udfile = udfilefor   ...  x.save()
            for el in elementos:
                el.udfile = ud  # Se asocia al fichero suyo
                el.save()
                #print(el)
            
    
    
    except Exception as e:
        LogError(descripcion=str(e),
                 accion='No se guarda el analisis py de la idcorreccion')
        raise

if __name__ == "__main__":
    
    import ast
    import astor
    fichero1 = '/home/chilli-mint/Dropbox/MiStuRe/misture_core/MISTURE/analyx' \
               '/git_utils.py'
    ruta_examen = '/home/chilli-mint/Desktop/examen/'
    '''
    import ast
    with open('/home/chilli-mint/Dropbox/_PFC_MISTURE/001_codigos_py_sh_etc
    /humansize.py') as fp:
        a = ast.parse(fp)
    
    for node in ast.walk(a):
        print(node)
    print()
    for node in ast.iter_child_nodes(a):
        print(node)
    '''
    
    # print(b)
    
    zz = False
    if zz:
    
        # a = astor.parsefile('/home/chilli-mint/Dropbox/_PFC_MISTURE
        # /001_codigos_py_sh_etc/humansize.py')
        a = astor.parsefile('/home/chilli-mint/Dropbox/MiStuRe/misture_core/'
                            + \
                            'MISTURE/analyx/git_utils.py')
        # print(a)
        # b = astor.to_source(a)
        print(type(ast.walk(a)))
        for node in ast.walk(a):
            # print(type(node), '->\t', astor.strip_tree(node))
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                # print(astor.code_to_ast.get_file_info(node))
                print(type(node), node.name, node.lineno, node.col_offset)
                print(node._fields)
                # if isinstance(node, ast.FunctionDef):
                # print(node.name, node.lineno, node.col_offset, node._fields)
                # print('####')
                # print(ast.dump(node, annotate_fields=True,
                # include_attributes=False))
    
    print('###############################')
    
    #funtionalality()
    