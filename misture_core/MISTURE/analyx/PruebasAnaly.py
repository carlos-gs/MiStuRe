#!/usr/bin/env python
# encoding: utf-8
'''
Integrar para las pruebas un sistema de sandboxing o algo equivalente.
IMPORTANTE: python3 instalado y python lance un interprete python2 (2.7 pref.)
'''
#import const
from analyx import OutputAnaly
import sys
import os
import re
import subprocess

from entities.pymdbodm import PruebaMisture, PruebaResultadoMisture





def ejecutar_prueba(rutabase, pruebas):
    """
    """
    OLDIR = subprocess.getoutput('pwd')
    try:
        os.chdir(rutabase)
    except:
        raise Exception('chdir error sobre: ' + rutabase + " \n")

    ######## TEST DE RESULTADOS DE EJECUCIONES DE LOS PROGRAMAS\n'
    resultados = []
    for prueba in pruebas:
        try:
            esperado = prueba.salida.copy()
            prueba = True
        except: # Prueba sin salida esperada
            prueba = False
            
        if prueba and not prueba.comando.endswith('&'):
            
            # Un & y un comando infinito puede bloquearo.
            (status, out) = subprocess.getstatusoutput(prueba.comando)
            
            # Se comprueba la salida de lineas de texto
            res = OutputAnaly.verifyMulti(out, prueba.salida.copy())
            
            resultados.append(PruebaResultadoMisture(prueba=prueba.pk,
                exito=res, status=status, salida=out.split()))
        else:
            os.system(prueba.comando)
            
            resultados.append(
                PruebaResultadoMisture(prueba=prueba.pk))
    os.chdir(OLDIR)
    return resultados
            
            

        


    



class ProgLanguage:
    """
       Contiene una estructura con lenguaje y versión major.minor.micro_serial
    """
    version = [x for x in sys.version_info[:3]]
    version.append(sys.version_info[4])
    language = 'python'
    _sepreg = '\.|_'
    
    def __init__(self, lang='', vers=''):
        if not lang and not vers:
            self.language = ProgLanguage.language
            self.version = ProgLanguage.version
        elif lang and vers and \
                re.match('^\d+\.\d+[\.\d+[_\d+]?]?', vers):
            self.language = lang
            self.version = self._vssplit(vers)
        else:
            raise Exception(__name__ + ".ProgLanguage bad params")
    
    def __str__(self):
        return self.language + ' ' + '.'.join(self.version[:3]) + \
               '_' + str(self.version[3])
    
    def __eq__(self, other):
        """
           Igualdad de valor si == language e iguales major y minor de la vs.
           @return: booleano si son el mismo lenguaje y la tupla versión.
        """
        return (type(self) == type(other) and \
                self.language.lower() == other.language.lower() and \
                self.version == other.version)

    def _vssplit(self, vsstr):
        vs = [int(x) for x in re.split(self._sepreg, vsstr, 3)]
        [vs.append(0) for i in range(4 - len(vs))]
        return vs
    
    def isEqUpperVersion(self):
        """
            Indica si es python con major y minor >= al que ejecutamos.
        """
        if ProgLanguage.language.lower() != self.language.lower():
            return False
        for i in range(3):
            if ProgLanguage.version[:2] > self.version[:2]:
                return False
            elif ProgLanguage.version[:2] < self.version[:2]:
                return True
        return True
    
    def isNowPyComp(self):
        """
           Compatibilidad python con la versión que ejecuta el script.
        """
        return self.version[0] == ProgLanguage.version[0] and \
               self.isEqUpperVersion()


class CheckTest:
    langVers = ProgLanguage('python', '2.7')
    
    def __init__(self):
        pass


if __name__ == "__main__":
    pass
    '''
    for x in sys.version_info:
        print(type(x), x)
    pl1 = ProgLanguage()
    pl2 = ProgLanguage("python", "3.4.0")
    pl3 = ProgLanguage("python", "3.4.1_1")
    try:
        pl4 = ProgLanguage("python", "3.4_0")
        print('troll')
    except:
        print('Error esperado probando un formato de versión incorrecto')
    for pl in (pl1, pl2, pl3):
        print('Es version superior mi ', pl.version, pl.isEqUpperVersion())
        print('Es version compatible mi ', pl.version, pl.isNowPyComp())
    print(pl1 == pl2, pl2 == pl3, pl1 == pl3)
    '''
