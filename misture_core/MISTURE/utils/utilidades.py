#!/usr/bin/env python3
# encoding: utf-8
"""
Created on 03/10/2014
@author: Carlos González Sesmero
"""

from math import sqrt, log10, ceil
import sys, os, re, datetime
from traceback import print_exc
import types as tp
import numpy as np  # bsd license?
from utils.filecorrector import ParNombres


class Chrono:
    """
        Cronómetros en seg para medir de forma aproximada -a partir de ms- el
        tiempo que se emplea en ejecutar entre dos puntos de la ejecución.
        Por el momento, no soporta cronometradas discontinuas de tiempo.
    """
    # CATEGORIAS DE CUENTAS DE TIEMPO PARA T_COUNT
    TTYPE_total = 'total' # De inicio a último
    TTYPE_splits = 'splits' # Lista de tiempo de intervalos
    TTYPE_splits_cum = 'splits_cum' # Lista desde inicio a fin de cada interv.

    def __init__(self):
        self.chronos = dict()

    def start(self, name):
        if name in self.chronos.keys():
            return False
        else:
            self.chronos[name] = [datetime.datetime.now()]
            return True

    def finish(self, name):
        tf = datetime.datetime.now()
        try:
            self.chronos[name].append(tf)
            # del(self.chronos[name])
            return True
        except KeyError:
            return False

    def t_count(self, name='', ttype='total'):
        '''
        Devuelve l
        :param name:
        :param ttype: Tipo de cuenta deseada. Literales Chrono.TTYPE_
        :return:
        '''
        try:
            times = self.chronos[name]
            if ttype == Chrono.TTYPE_total:
                # Tiempo global.
                tick_count = len(times)
                if tick_count in (0, 1):
                    return None
                return (times[len(times) - 1] - times[0]).total_seconds()
            #  Tiempos de cada parcial disponible
            elif ttype == Chrono.TTYPE_splits:
                return [(v[1]-v[0]).total_seconds()
                        for k, v in self.chronos.items()]
            #  Tiempos totales para cada parcial
            elif ttype == Chrono.TTYPE_splits_cum:
                return sum(self.t_count(name, Chrono.TTYPE_splits))
            else:
                return None
        except KeyError:
            return None
        except IndexError:
            return None


def addErrorToFiles(error_msg, *error_files, in_strerr=True):
    """
    Método para volcar texto (de error) a los logs/ficheros indicados, y
    a stderr por defecto aunque de forma opcional.
    :param error_msg: texto para describir el error
    :param error_files: rutas de ficheros de error/logs donde volcarlo.
    :param in_strerr: se indica si se imprime por la salida de error
    :return: sin retorno, de momento imprime trazas si yerra writeFiles
    """
    if in_strerr:
        print(error_msg, file=sys.stderr)
    writeFiles(error_msg, *error_files)


def writeFiles(msg, *files):
    """
    Método usado a lo largo del proyecto para hacer escrituras aditivas

    :param msg: texto a añadir al final del fichero/s
    :param files: rutas absolutas del fichero/s
    :return: sin retorno, de momento imprime trazas en caso de error.
    """
    for file in files:
        if os.access(str(file), os.W_OK):
            with open(str(file), 'a') as fd:  # file supports c.m.p.
                fd.write(msg + '\n')
                # fd.close()  unnecesary cause with + file object
        else:
            print(__name__ + ".writeFiles error writing: " + file + "\n")
            print_exc()


def readFileFull(path):
    """
    RETORNA EL VOLCADO ENTERO DE UN FICHERO DE TEXTO.
    Función usada a lo largo del proyecto para la lectura de ficheros de
    texto con código fuente, logs, ...
    :param path: ruta absoluta del fichero (de texto) a leer.
    :return: de momento, el contenido del fichero completo.
    """
    if os.access(path, os.R_OK):
        # ISO-8859-1 utf-8 surrogateescape ommits encoding errors
        with open(path, "r",
                  errors='surrogateescape') as fd:  # file supports c.m.p.
            result = fd.read(None)
            # fd.close()  unnecesary cause with + file object
    else:
        print(__name__ + ".readFileFull error reading: " + path + "\n")
        print_exc()
    return result


def d_levenshtein(str1, str2):
    """
    Algoritmo que calcula el mínimo número de operaciones de borrado
    insercción y cambio necesarios que separan a dos strings
    Fuente del algoritmo: wikipedia.
    :param str1:
    :param str2:
    :return Número entero con dicha cantidad mínima
    """
    d = dict()
    for i in range(len(str1) + 1):
        d[i] = dict()
        d[i][0] = i
    for i in range(len(str2) + 1):
        d[0][i] = i
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            d[i][j] = min(d[i][j - 1] + 1, d[i - 1][j] + 1,
                          d[i - 1][j - 1] + (not str1[i - 1] == str2[j - 1]))
    return d[len(str1)][len(str2)]


# DISTANCIAS DISCRETAS H,V RESPECTO a EN UN TECLADO CON DISTRIBUCION ESPAÑOLA
# Para calcular distancias, desplazar la referencia n veces la max separación.
DIST = {'a': (0, 0), 's': (1, 0), 'd': (2, 0), 'f': (3, 0), 'g': (4, 0),
        'h': (5, 0), 'j': (6, 0), 'k': (7, 0), 'l': (8, 0), 'ñ': (9, 0),
        'q': (0, 1), 'w': (1, 1), 'e': (2, 1), 'r': (3, 1), 't': (4, 1),
        'y': (5, 1), 'u': (6, 1), 'i': (7, 1), 'o': (8, 1), 'p': (9, 1),
        'z': (0, -1),
        'x': (1, -1), 'c': (2, -1), 'v': (3, -1), 'b': (4, -1), 'n': (5, -1),
        'm': (6, -1), '_': (9, -1), '-': (9, -1), '.': (7, -1), ',': (7, -1),
        '1': (0, 2), '2': (1, 2), '3': (2, 2), '4': (3, 2), '5': (4, 2),
        '6': (5, 2),
        '7': (6, 2), '8': (7, 2), '9': (8, 2), '0': (9, 2), '(': (7, 2),
        ')': (8, 2),
        '~': (3, 2)
        }
"""
    @attention: Coordenadas que expresan la separación 2D en teclado español.
"""


def valueDist(char='a', bias=100):
    """
    Calculo de la distancia de un caracter de teclado, a partir de un dict
    DIST, cuyas claves son carácteres y valores una 2-tupla de números.
    :param char: caracter
    :param bias: desviacion aplicada a cada componente respecto a la referencia.
    La idea es que alejar la referencia para que los caracteres queden
    alejados -aprox.- por igual (distancias absolutas aumentan, se comprimen
    las relativas entre teclas si la referencia de DIST era.
    :return:
    """
    x, y = DIST[char]  # Diccionario de Coordenadas 2D de distancia.
    val = 2 * bias ** 2 if x is None else ((bias + x) ** 2 + (bias + y) ** 2)
    return sqrt(val)


def CorrCoef2(str1, str2, fvalor=ord, fpadear=lambda w: 0):
    """Coeficiente de correlación entre dos strings con asignación
    de función de valor de sus carácteres y de valor de rellenado
    de string (para igualar longitud de str1 y str2).
    :param str1:
    :param str2:
    :param fvalor: función de un parámetro de tipo char que retorne nº
    :param fpadear: función de un parámetro string que retorne nº
    :return:
    :raise: si tipos no concuerdan o los parámetros de las funciones pasadas.
    """

    # Se verifican los tipos str y los tipos que nos valen como funcion.
    funtipos = (tp.FunctionType, tp.BuiltinFunctionType, tp.MethodType,
                tp.BuiltinMethodType, tp.LambdaType)
    if not all([isinstance(x, funtipos) for x in (fvalor, fpadear)]):
        raise Exception(__name__ +
                        '.corrCoef2 fvalor and fpadear must be functions')
    if False in [type(x) for x in (str1, str2)]:
        raise Exception(__name__ + '.corrCoef2 str1 and str2 must be str')
    # Se prepara una matriz de palabras. Cada carácter pasa a fvalor(char)
    ls = (str1, str2)
    lenmax = max(len(word) for word in ls)
    words = [[fvalor(ch) for ch in word] for word in ls]
    '''Padear el str mas corto hasta la longitud del largo,
     aplicando fpadear sobre word para determinar que relleno corresponde.'''
    for word in words:
        for i in range(len(word), lenmax):
            word.append(fpadear(word))
    wordsarray = np.array(words)
    # #  Coeficientes de correlacion (matriz simétrica 2x2)
    coeficiente = abs(np.corrcoef(wordsarray)).tolist()
    return coeficiente[0][1]


def qsort(L):
    """
       Ordenar una lista de tuplas (float, elem) por menor float
    """
    if isinstance(L, list):
        raise Exception("qsort: L debe ser una lista")
    if not L:
        return []
    return qsort([x for x in L[1:] if x[0] < L[0][0]]) + L[0:1] + \
        qsort([x for x in L[1:] if x[0] >= L[0][0]])


def _debug_subswords_medidas(ltuplas):
    """Solo para debug subsWords, imprime calculos para cada par de nombres

    :param ltuplas: lista con las tuplas con el par de nombres y los valores
    :return:
    """
    # Orden: L1 buscada,measure, L3 buscada,levenshtein.
    l1 = sorted(ltuplas, key=lambda reg: (reg[0], int(reg[9])))
    l2 = sorted(ltuplas, key=lambda reg: (int(reg[9])))
    l3 = sorted(ltuplas, key=lambda reg: (reg[0], reg[2]))
    l4 = sorted(ltuplas, key=lambda reg: (reg[2]))
    for lista in (l1, l2, l3, l4):
        print('BUSCADA'.rjust(35), 'CANDIDATA'.ljust(35), 'LEV'.rjust(3),
              'MEDIDA'.ljust(10), 'LEVLOG'.ljust(10), 'CORRLOG'.ljust(10),
              'MAXCORR'.ljust(10), 'UMBRAL'.ljust(10))
        print('-'.rjust(35,'-'), '+'.rjust(35,'+'), '-'.rjust(3,'-'),
              '+'.ljust(10,'+'), '-'.ljust(10,'-'), '+'.ljust(10,'+'),
              '-'.ljust(10,'-'), '-'.ljust(10,'-'))
        #  'ORD 0PAD'.ljust(10), 'SPA 0PAD'.ljust(10),
        #  'ORD MEAN'.ljust(10), 'SPA MEAN'.ljust(10), )
        for mt in lista:
            numeros = [mt[9], mt[7], mt[8], max(mt[3], mt[4], mt[5], mt[6]),
                       mt[10]]
            num2 = [str(round(x, 4)).ljust(10) for x in numeros]
            print(mt[0].rjust(35), mt[1].rjust(35), str(mt[2]).rjust(3), *num2)
        print('#'.rjust(135, '#'))


def subsWords(buscadas, candidatas):
    """Asigna elementos de la lista, pasada como primer parámetro, con la
       segunda, si cumplen unos umbrales mínimos de semejanza, basados
       en el cálculo de la distancia de levenshtein y coeficientes de
       correlación, calculados según diferentes funciones valor
       de los caracteres de las cadenas y de relleno hasta igualar longitud.

    """
    if not type([]) in (type(buscadas), type(candidatas)):
        raise Exception(__name__ + ".subsWords: params not valid")
    if len(buscadas) == 0:
        return []

    lbuscadas = set(buscadas)
    lcandidatas = set(candidatas)
    print("Faltan: ", lbuscadas)
    print("Candidatos", lcandidatas)

    def mean_fun(w: str) -> float:
        return sum(w) / len(w)

    def val_b100(ch: str) -> float:
        return valueDist(ch, 1000)

    #  Constantes para el calculo del umbral.
    k1 = 100
    c1 = 1
    refcorr = 2/3  # corr_min_abmisible [0,1]
    cutlev = 1/4  # Sobre la min(len(str)) del par de nombres


    sol = set()
    [sol.add((b, c)) for c in lcandidatas for b in lbuscadas if b == c]
    for b in lbuscadas.copy():
        for c in lcandidatas.copy():
            if b==c:
                sol.add((b, c))
                lbuscadas.remove(b)
                lcandidatas.remove(c)

    medidas = []  # Tupla de (int, (str, str))
    rechazos = []
    MEGALIS = []

    for busc in lbuscadas:
        for cand in lcandidatas:
            par = (busc, cand)

            longmax = max(1, max(len(cand), len(busc)))
            umbral = c1 * k1 * k1 * (-log10(1-cutlev))

            #  Calculo de distancia y varias correlaciones.
            ldist = d_levenshtein(busc, cand)
            e = CorrCoef2(busc, cand)  # ord coef_corr padding 0
            f = CorrCoef2(busc, cand, fvalor=val_b100)  # spa 0-padding
            g = CorrCoef2(busc, cand, fpadear=mean_fun)  # ord mean-padding
            h = CorrCoef2(busc, cand, fvalor=val_b100, fpadear=mean_fun)
            # TODO: MEDIDA para comparar con umbral es la diferencia
            # Entre levenshtein y varias correlaciones propuestas.
            correlacion = max(e, f, g, h)
            levlog = k1 * log10(ldist) / log10(longmax)
            corrlog = k1 * log10(correlacion) / log10(refcorr)
            measure = levlog * corrlog

            MEGALIS.append([busc, cand, ldist, e, f, g, h,
                           levlog, corrlog, measure, umbral])
            medidatup = (par, measure, ldist, correlacion)

            # Agregar a candidatas si cumple las condiciones mínimas.
            if (measure < umbral) or (correlacion >= refcorr) or \
                    (ldist < ceil(cutlev * min(len(busc), len(cand))) + 1):
                medidas.append(medidatup)
            else:
                rechazos.append(medidatup)
    _debug_subswords_medidas(MEGALIS)
    # medidas.reverse() # se ordenaran por el primer campo (el valor de measure)
    # lord = qsort(medidas)
    pares_ord = sorted(medidas, key=lambda tup: (tup[1], tup[2], -tup[3]))
    #pares_ord = sorted(medidas, key=lambda tup: (tup[0][0], tup[1], tup[2], -tup[3]))

    pares_rec = sorted(rechazos, key=lambda tup: (tup[1], tup[2], -tup[3]))
    # Asignación substituciones soluciones.
    for lll in (pares_ord, ):
        for nombres, m, l, c in lll:
            print(str(round(m, 3)).ljust(10), '\t', str(round(c, 3)).ljust(10),
                  '\t', str(l).rjust(2) , '\t',  nombres)
        print('#'.ljust(50, '#'))

    while pares_ord:
        names, med, lev, ccorr = pares_ord.pop(0)
        sol.add(names)
        i = 0
        lg = len(pares_ord)
        while i < lg:
            elem = pares_ord[i]
            if elem[0][0] == names[0] or elem[0][1] == names[1]:
                pares_ord.pop(i)
                lg -= 1
            else:
                i += 1
    return sol


def crearsolucion(pares_ord):
    GRUPOS = {}
    BUSCADAS = set()
    CANDIDATAS = set()
    # Separamos los pares candidatos en grupos, según su buscada.
    for pn in pares_ord:
        b = pn.buscada
        c = pn.candidata
        if b in GRUPOS:
            GRUPOS[b].append(pn)
        else:
            GRUPOS[b] = [pn]
        BUSCADAS.add(b)
        CANDIDATAS.add(c)

    SOLUCION = []
    #Construimos tupla solucion.
    for grupob in GRUPOS.values():
        for pn in grupob:
            if not any([pn.candidata == pnaux.candidata for pnaux in SOLUCION]):
                pass
    return


def recursolucion(solucion, grupos):
    solpre = solucion.copy()


def construirsolucion(pares_ord, sol):
    if not isinstance(sol, set):
        raise Exception('sol debe ser un conjunto')
    while pares_ord:
        names, med, lev, ccorr = pares_ord.pop(0)
        sol.add(names)
        i = 0
        lg = len(pares_ord)
        while i < lg:
            elem = pares_ord[i]
            if elem[0][0] == names[0] or elem[0][1] == names[1]:
                pares_ord.pop(i)
                lg -= 1
            else:
                i += 1
    return sol


def subsWords_v2(buscadas, candidatas, suptrivial=True):
    """Asigna elementos de la lista pasada como primer parámetro con la
       segunda, si cumplen unos umbrales mínimos de semejanza basados
       en el cálculo de la distancia de levenshtein y coeficientes de
       correlación calculados según diferentes funciones valor
       de los caracteres de las cadenas y de relleno hasta igualar longitud.

    """
    if not type([]) in (type(buscadas), type(candidatas)):
        raise Exception(__name__ + ".subsWords: params not valid")
    if len(buscadas) == 0:
        return []

    lbuscadas = set(buscadas)
    lcandidatas = set(candidatas)

    # Funciones para padear nombres y asignar un valor a un carácter.
    def mean_fun(w: str) -> float:
        return sum(w) / len(w)

    def val_b100(ch: str) -> float:
        return valueDist(ch, 1000)

    #  Constantes para el calculo del umbral.
    k1 = 100
    c1 = 1
    refcorr = 2/3  # coloca el k1*1 de corrlog a esa corr [0,1]
    cutlev = 1/4  # Proporcion sobre la min(len(str)) del par de nombres

    sol = set()  # Inicializa el conjunto solucion
    # Se apuntan las soluciones triviales y se quitan de los conjuntos.
    if not suptrivial:
        [sol.add((b, c)) for c in lcandidatas for b in lbuscadas if b == c]
        for b in lbuscadas.copy():
            for c in lcandidatas.copy():
                if b == c:
                    sol.add((b, c))
                    lbuscadas.remove(b)
                    lcandidatas.remove(c)

    medidas = []  # Lista de ParNombre
    rechazos = []

    for busc in lbuscadas:
        for cand in lcandidatas:
            # Si la trivial no interesa, saltamos el caso.
            if suptrivial and busc == cand:
                continue

            # Optimización: si tenemos un par y su reflexiva, duplicar el
            # par con sus nombres cambiados en la lista de medidas/rechazos
            # ... continue

            longmax = max(1, max(len(cand), len(busc)))
            umbral = c1 * k1 * k1 * (-log10(1-cutlev))

            #  Calculo de distancia y varias correlaciones.
            ldist = d_levenshtein(busc, cand)
            e = CorrCoef2(busc, cand)  # ord coef_corr padding 0
            f = CorrCoef2(busc, cand, fvalor=val_b100)  # spa 0-padding
            g = CorrCoef2(busc, cand, fpadear=mean_fun)  # ord mean-padding
            h = CorrCoef2(busc, cand, fvalor=val_b100, fpadear=mean_fun)

            correlacion = max(e, f, g, h)
            levlog = k1 * log10(ldist) / log10(longmax)
            corrlog = k1 * log10(correlacion) / log10(refcorr)
            measure = levlog * corrlog  # medida segun levenstein y corrs.

            objmedidas = ParNombres(busc, cand, levdis=ldist,
                ord_0_corr=e, spa_0_corr=f, ord_mean_corr=g, spa_mean_corr=h,
                max_corr=correlacion, lev_log=levlog, corr_log=corrlog,
                measure=measure)
            objmedidas.nuevoorden('buscada', 'candidata', 'levdis', 'measure')

            # Agregar a candidatas si cumple las condiciones mínimas.
            if (measure < umbral) or (correlacion >= refcorr) or \
                    (ldist < ceil(cutlev * min(len(busc), len(cand))) + 1):
                medidas.append(objmedidas)  # medidatup)
            else:
                rechazos.append(objmedidas)  # medidatup)

    # Ordenar e imprimir tuplas.
    if medidas:
        medidas_ord = sorted(medidas, key=lambda el: el._clave())
        print(medidas[0]._reprRow(True))  # Para depurar, las cabeceras.
        for pn in medidas_ord:
            print(pn._reprRow())
    print('#'.ljust(100, '#'))
    if rechazos:
        rechazos_ord = sorted(rechazos, key=lambda el: el._clave())
        print(rechazos[0]._reprRow(True))  # Para depurar, las cabeceras.
        for pn in rechazos_ord:
            print(pn._reprRow())

        # Selección de la combinación entre las soluciones.
        #construirsolucion(pares_ord, sol)
    #crearsolucion(medidas_ord)

    return sol


if __name__ == "__main__":

    def test_subsWords():
        buscadas2 = ['mifichero.py', 'calcu.py', 'ficheroplus.py',
                    'mificheroplus.py']

        tenidas2 = ['ficheromi.py', 'calci.py', 'calcu.py~', 'mifichplus.py',
                   'mifichero.py'
                   ]
        buscadas = ['mifichero.py', 'calcu.py', 'ficheroplus.py',
                    'mificherocalcuplusobjetosputon.py', 'hichero.py',
                    'hifichero.py']


        tenidas = ['mificherocalcuplusobjetos.py', 'calciplus.py',
               'mufichero.py', 'mfichero.py', 'ifichero.py', 'mficheroi.py',
               'qficheroz.py',
               'nifichero.py', 'jifichero.py', 'kyfichero.py',
               'qifichero.py',
               'nuduxgwei,ot', 'nugoxjep,ou', 'njgjdifsp,qz', 'ogovjrp-pu',
               'calci.py', 'calc.py', 'jgjdifsp,qz',
               'ficherpplus.py', 'mficheropls.py'
               ]
        #tupla = subsWords_v2(buscadas, tenidas)
        palas = ['suma.py', 'calcsuma.py', 'calcobj.py', 'calcpoo.py']
        tupla = subsWords_v2(palas, palas)
        for name1, name2 in tupla:
            print(name1, '->', name2)
    # TODO PENDIENTES TAREAS PREPROCESAMIENTO, IDEAR CORRECCION SENCILLA
    # DE NOMBRES DE FICHEROS DE MISMA EXTENSION SI FALTAN Y SOBRAN.
    #test_subsWords()
    """
    pareja = ParNombres('buscada', 'candidata')
    pareja2 = ParNombres('buscada', 'candidata', medida=7)
    pareja3 = ParNombres('buscada2', 'candidata')
    print("Comparamos igualdad de parejas: ",
          pareja.esnombresiguales(pareja2), pareja2.esnombresiguales(pareja3))

    pareja3.creamedidas(correlacion=1, levenshtein=10)
    #print(pareja, '\n',pareja2,'\n' ,pareja3)
    import time
    time.sleep(1)
    pareja3.nuevoorden('correlacion', '-levenshtein')
    pareja3.nuevoorden('-correlacion', '-levenshtein')
    pass
    """




