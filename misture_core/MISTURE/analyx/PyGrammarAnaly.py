#!/usr/bin/env python
# encoding: utf-8

# -*- coding: iso-8859-15 -*-
'''
PyfichAnaly -- shortdesc
PyfichAnaly is a description
It defines classes_and_methods
@author:     user_name
@copyright:  2014 organization_name. All rights reserved.
@license:    license
@contact:    user_email
@deffield    updated: Updated
'''

import os
import re
import sys
import ast
import astor
import linecache
import os.path as op
import subprocess

import utils.utilidades as mutils
from entities.pymdbodm import Udfuente, Udfuentecoor, LogError



NUMLINEAS_SNIPPED = 12

def leerlineasfichero(ruta, nlinea, nlin):
    lineas = linecache.getlines(ruta)[nlinea:nlinea + nlin]
    return lineas


def snippedfichero(ruta, nini, nlin):
    lines = []
    with open(ruta) as fp:
        for i, line in enumerate(fp):
            if nini - 1 > i:
                continue
            elif nini - 1 <= i < nini + nlin - 1:
                lines.append(line)
            elif i >= nini + nlin - 1:
                break
    return ''.join(lines)


def analy_pygrammar(ruta):
    resultado = []
    if not op.exists(ruta):
        raise Exception('PyGrammarAnaly Error: no existe ' + str(ruta))
    try:
        # PARA LAS PRACTICAS DE PYTHON2, LAS RECODIFICAMOS Y PASAMOS A PY3
        # PARA PODER ANALIZAR SU ARBOL
        (status0, out0) = subprocess.getstatusoutput(" echo '\n' >> " + ruta)
        (status1, out1) = subprocess.getstatusoutput(
            """cat {0} | sed "s/á/a/g;s/é/e/g;s/í/i/g;s/ó/o/g;s/ú/u/g" \
            > {0}.bak && mv {0}.bak {0}""".format(ruta))
        (status2, out2) = subprocess.getstatusoutput(" 2to3 -w " + ruta)
    
        if any((status0, status1, status2)):
            LogError(descripcion='analy_pygrammar fichero no se analiza'
                                 'por problemas codificacion ' + ruta)
            return resultado
            #raise Exception('Error al convertir a py3 ' + ruta)
        # Analisis del abstract source tree para py3
        ast_tree = astor.parsefile(ruta)
        for nd in ast.walk(ast_tree):
            if isinstance(nd, (ast.ClassDef, ast.FunctionDef)):
                # print(astor.code_to_ast.get_file_info(nd))
                # print(type(nd), nd.name, nd.lineno, nd.col_offset)
                coor = Udfuentecoor(filaini=nd.lineno, col=nd.col_offset)
                elem = Udfuente(nombre=nd.name, ubicacion=coor)
                
                if isinstance(nd, ast.ClassDef):
                    elem.tipo = Udfuente.TIPO_CLASE
                elif isinstance(nd, ast.FunctionDef):
                    elem.tipo = Udfuente.TIPO_FUNC
                
                elem.snipped = snippedfichero(ruta, nd.lineno,
                                              NUMLINEAS_SNIPPED)
                
                resultado.append(elem)
        return resultado
    except Exception as exc:
        raise
    
    return





###############################################################################

# PATRONES. Usar flag re.M en las funciones para considerar ^$inicio/fin linea
# No son exhaustivos para toda la sintáxis posible en python
def namerPatvars(name):
    if not type(name) is str:
        return r""
    NAMEPAT = r"\s*(?P<" + name + ">[_A-Za-z][_A-Za-z0-9]*)\s*"
    return NAMEPAT
#NAMEPAT = r"\s*(?P<" + name + ">[_A-Za-z][_A-Za-z0-9]*)\s*"
#PARAMPAT = r"\s*(?:[_A-Za-z][_A-Za-z\d]*){0,1}\s*"
#INTLINE = r"\s*\\\n" # '  \\n'
CLASSPAT = r"^class\s+" + namerPatvars('class') + r"(?:\([^\(]*\)){0,1}\s*:\s*"
FUNCPAT = r"^def\s+" + namerPatvars('function') + r"(?:\([^\(]*\)){0,1}\s*:\s*"
METHPAT = r"^\s+def\s+" + namerPatvars('method') + r"(?:\([^\(]*\)){0,1}\s*:\s*"
MAINPAT = '|'.join((FUNCPAT, CLASSPAT, METHPAT))


class PyModuleCont(object):
    """
        Navegador del diccionario que representan los elementos de código dentro
        de un módulo python.
    """
    
    def __init__(self, strpycode):
        """
            Find main elements of code such class, class def and
            module def and extracts their names.
        """
        self.elements = {
            'class': [],
            'function': [],  # 'Methods' doesn't associated by classes
            'method': [],  # Methods associated by classes
            # 'inherit': []
        }
        pyregex = re.compile(MAINPAT, re.M)
        # print( re.findall(MAINPAT, strpycode, re.M))
        s = pyregex.search(strpycode)  # re.M multiline
        while (s):
            for x in self.getTypes():
                try:
                    name = s.group(x)
                except IndexError:  # cause not all keys be in CLASSREGEX PAT
                    # print('PyfichAnaly:PyModuleCont: raises IndexError')
                    continue
                if name:
                    self.elements[x].append(name)
            # Evaluate rest of code without trunc strpycode string
            s = pyregex.search(strpycode, s.end())
    
    def getElemsByType(self, etype):
        try:
            return self.elements[etype]
        except KeyError:
            return None
    
    def getTypes(self):
        return self.elements.keys()
    
    def getNumElemType(self, etype):
        elemlist = self.getElemsByType(etype)
        if not elemlist:
            return -1
        return len(elemlist)


def analy_pyfiles(studentObj, FILES, PYFILES):
    """
    Algoritmo de identificación de elementos de código a través de patrones
    regulares.
    """
    # Rutas de los directorios y ficheros
    repositorypath = studentObj.gitPath
    resultsfilepath = studentObj.resultPath
    errorfilepath = studentObj.errorPath
    teacherfilepath = studentObj.teachPath
    
    pydata = {}  # It will anotes
    # print('Analizando:\t' + repositorypath + '\n')
    try:
        # Cuando este ligado al repo git vendran de los análisis de
        repfiles = os.listdir(repositorypath)
    except:
        error = 'Error al evaluar los ficheros del repositorio'
        studentObj.writeErrLogs(error)
        print(error)
        return None
    if not repfiles:
        error = 'No hay ficheros en el repositorio'
        studentObj.writeErrLogs(error)
        print(error)
        return None
    # # Renombrado heuristico de ficheros sobrantes de ambas listas
    # Obtenemos listas de buscados no encontrados y encontrados no buscados.
    fcandidatos = repfiles.copy()
    fbuscados = FILES.copy()
    for fb in FILES:
        for fc in repfiles:
            if fb == fc:
                fbuscados.remove(fb)
                fcandidatos.remove(fb)
    # tuplas de renombrado, renombramos y agregamos a repfiles.
    renames = mutils.subsWords(fbuscados, fcandidatos)
    for tup in renames:
        fb = tup[0]
        fc = tup[1]
        if fb[max(len(fb) - 3, 0):] == fc[max(len(fc) - 3, 0):]:  # == extension
            origen = repositorypath + '/' + fc
            destino = repositorypath + '/' + fb
            os.system("mv {} {}".format(origen, destino))
            repfiles.append(tup[0])
            print('Renombrado {} {}'.format(origen, destino))
    for f in FILES:
        if f not in repfiles:
            studentObj.writeErrLogs('Filename not found: ' + f)
    # Analizamos cuantos ficheros de los esperados hay en el repo.
    numfilesok = 0
    for f in repfiles:
        if f not in FILES:
            continue
        numfilesok += 1
        if f in FILES and re.search('.py$', f):
            pyfpath = repositorypath
            if not re.search('/$', repositorypath):
                pyfpath += '/'
            try:
                # CODIGO A UN STRING, OJO CON FICHEROS GRANDES.##########
                code = mutils.readFileFull(pyfpath + f)
                # Analysis python code: number
                pydata[f] = PyModuleCont(code)
            except:
                studentObj.writeErrLogs(
                    'Error MainAnaly.analy_pyfiles, leyendo {0}, ' +
                    'ocurrió:\n {1} '.format(pyfpath + f, sys.exc_info()))
    # OBTENCION DE RESULTADOS Y REPRESENTACION
    outputstr = '\n########### COMPROBACIONES DE FICHEROS ENTREGADOS ######\n'
    outputstr += 'Ficheros entregados con exito: ' + str(numfilesok) + \
                 ' sobre ' + str(len(FILES)) + '.\n'
    outputstr += 'Modulos .py entregados con exito: ' + str(len(pydata)) + \
                 ' sobre ' + str(len(PYFILES)) + '.\n'
    # Extraemos los datos clave de cada fichero .py
    for fich in pydata.keys():
        # print(pydata[fich].elements)
        outputstr += 'MODULO ' + fich + '.\n'
        typs = pydata[fich].getTypes()
        for elem in typs:
            for name in pydata[fich].getElemsByType(elem):
                outputstr += '\t' + elem + ':\t' + name + '\n'
    outputstr += '\n'
    studentObj.writeResultStud(outputstr)


###############################################################################




if __name__ == "__main__":
    pass
