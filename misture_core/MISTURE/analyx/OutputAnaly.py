#!/usr/bin/env python
# encoding: utf-8
'''
OutputAnaly -- P2 PTAVI FUNCTIONS THAT EVALUATE STRINGS AT OUTPUT
                OF P2 EXEC WITH EXPECTED OUTPUTS (SOMEONE APROX., OTHERS EQUAL)

OutputAnaly es un módulo que recoje métodos y funciones relacionados
con la verificación de sálidas de programas (de texto, etc) de acuerdo
con unos resultados previstos.

It defines classes_and_methods

@author:     Carlos González Sesmero.

@copyright:  2014.

@license:    license

@contact:    gcarlosonza@gmail.com
@deffield    updated: Updated
'''

import re


def verifySimple(strout, strexpec):
    """
        Verifica una línea de salida de texto con una línea esperada.
        @param strout: string
        @param strexpec: string
    """
    # print('#>' + re.escape(strout)  + '<#')
    # print('#>' + strexpected + '<#')
    # print('\n')
    # print('>>> ' + strout + " <<<")
    if re.search(re.escape(strexpec), strout, re.I):
        return True
    return False


def verifyMulti(strout, tupexpec):
    """
        Verifica una salida de texto multilínea con
        una tupla de líneas prevista dada.
        @param strout: string
        @param tupexpec: string
    """
    checklist = []
    lines = re.split('\n', strout)
    ntest = len(tupexpec)
    if (len(lines) < ntest):
        return False
    for p in range(ntest):
        checklist.append(verifySimple(lines[p], tupexpec[p]))
    for check in checklist:
        if not check:
            return False
    return True

