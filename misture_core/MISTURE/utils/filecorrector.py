# coding=utf-8

import sys
#sys.path.append('/home/chilli-mint/Dropbox/MiStuRe/misture_core/MISTURE')

import abc  # abstractmethod
import collections
from utils.utilidades import * #CorrCoef2,  d_levenshtein, valueDist
from math import log10, ceil
from numbers import Number




class ParNombres:
    """
    Almacen de 2 cadenas de texto junto con atributos, de
    creación dinámica, que representan MEDIDAS que relacionan ambas cadenas, la
    cadena buscada y la candidata a serlo.
    Puede indicar un valor de...

    """
    keybuscada = "buscada"
    keycandidata = "candidata"

    # @classmethod
    def clavesorted(obj):
        """Para un obj de esta clase, es una función compatible con la admitida
        por el arg key del built-in sorted para listas (de ParNombres).
        Si se intenta hacer un sorted con ParNombres de diferente _orden, no
        hay error, pero el ordenamiento será incorrecto => Solución, encapsular
        esta fun con otra que invoque el metodo nuevoorden antes, sobre una
        copia de obj, con el mismo orden para todos.

        :return: tupla proporcionada por el método _clave()
        """
        if not isinstance(obj, ParNombres):
            raise Exception(__name__ + '.ParNombres.clavesorted(obj) error')
        obj._clave()

    def __init__(self, buscada, candidata, **medidas):
        self.buscada = buscada
        self.candidata = candidata
        self._orden = []
        self._medkeys = []
        self.creamedidas(**medidas)
        pass

    def getbuscada(self):
        # TODO: Mejorarlo a http://www.python-course.eu/python3_properties.php
        return str(self.buscada)

    def getcandidata(self):
        # TODO: Mejorarlo a http://www.python-course.eu/python3_properties.php
        return str(self.candidata)

    def getmedida(self, nombre):
        # TODO: Mejorarlo a http://www.python-course.eu/python3_properties.php
        if nombre not in self._medkeys:
            return None
        valor = getattr(self, nombre)
        tipo = type(valor)
        if tipo == str:
            return str(valor)
        elif isinstance(valor, Number):
            return valor
        else:
            return valor  # TODO: Cambiarlo por copia o clonar objetos.

    def _getattr(self, nombre):
        """Devolvemos el attr indicado por nombre si esta entre los
        significativos para este objeto de _medkeys, o 'buscada' o 'candidata'.

        :param nombre:
        :return:
        """
        if nombre in self._medkeys or nombre in (ParNombres.keybuscada,
                                                 ParNombres.keycandidata):
            return getattr(self, nombre, None)
        return None

    def esnombresiguales(self, pnobject):
        if not isinstance(pnobject, ParNombres):
            raise Exception('Parametro debe ser del tipo ParNombres')
        return self.getcandidata() == pnobject.getcandidata() and \
            self.getbuscada() == pnobject.getbuscada()

    def esbuscada(self, buscada):
        if not isinstance(buscada, str):
            raise Exception('Parametro debe ser del tipo str')
        return self.getbuscada() == buscada

    def escandidata(self, candidata):
        if not isinstance(candidata, str):
            raise Exception('Parametro debe ser del tipo str')
        return self.getcandidata() == candidata

    def nuevoorden(self, *camposstr):
        """Se le pasan los nombres de las medidas, o buscada o candidata,
        por los que _clave producirá una tupla de ordenamiento del objeto.
        Dos objetos ParNombres con diferencias en nombres de medidas, tipos,
        u orden, pueden resultar ordenamientos malos u incluso excepciones.
        Se puede preceder un - para indicar un orden
        descendente, si el campo es numérico.

        :param camposstr:
        :return:
        """
        orden = []  # Nuevo orden provisional.
        for cp in camposstr:
            if not isinstance(cp, str):
                raise Exception('Campo {} no es {}.'.format(cp, 'str'))
            if cp[0] == '-':
                desc = True
                cpname = cp[1:]
            else:
                desc = False
                cpname = cp
            if self._esmedida(cpname) or cpname in ('buscada', 'candidata'):
                valorcampo = self.getmedida(cpname)
            else:
                raise Exception('{} no es propiedad reconocida.'.format(cpname))
            if desc and not isinstance(valorcampo, Number):
                raise Exception('{} no numérico para -.'.format(cpname))
            orden.append(cp)  # Agregamos al nuevo orden provisional.
        # Sustituimos el viejo orden.
        self._orden.clear()
        self._orden.extend(orden)

    def creamedidas(self, **medidas):
        """Insertamos medidas a ParNombres, con el nombre dado a los args
        y el valor de estos argumentos. Pisa si ya existía. El nombre de la
        medida se rechaza si colisiona con cualquier atributo que no es medida.

        :param medidas:
        :return:
        """
        for k, v in medidas.items():
            if k not in self._medkeys and k in dir(self):
                raise Exception('{} nombre no valido por colisión'.format(k))
            setattr(self, k, v)
            self._medkeys.append(k)

    def _esmedida(self, nombre):
        if not isinstance(nombre, str):
            raise Exception('El parámetro debe ser {}'.format('str'))
        if nombre in self._medkeys:
            return True
        return False

    def _clave(self):
        """Retorna una tupla con los valores de los campos de ParNombre en
        el orden proporcionado por el atributo _orden. Estos campos pueden
        ser las medidas, buscada o candidata. - solo soporta numericos

        :return: tupla con los valores de los campos que indica _orden
        """
        valores_ord = []
        for at in self._orden:
            if at[0] == '-':
                valores_ord.append(- self._getattr(at[1:]))
            else:
                valores_ord.append(self._getattr(at))
        return tuple(valores_ord)

    def _reprRow(self, cabeceras=False):
        """Esta hecho un poco triki, lo uso para depurar iterables de
        ParNombre semejantes, e imprimir una línea de cabecera con los
        nombres de los campos ordenados que se van a imprimir sucesivamente.

        :return:
        """
        texto = ''
        for ind, valor in enumerate(self._clave()):
            # Adecuamos el valor para su representacion str.
            if isinstance(valor, str):
                stvalor = valor[:35]
                just = 35  # Cantidad de caracteres de justificado.
            elif isinstance(valor, int):
                stvalor = str(valor)
                just = 5
            elif isinstance(valor, float):
                stvalor = str(round(valor, 5))
                just = 11
            elif isinstance(valor, Number):
                stvalor = str(valor)
                just = 20
            else:
                stvalor = str(valor)
                just = 30
            if cabeceras:
                valorpr = self._orden[ind]  # nombre y valor coinciden por ind
                texto = texto + '\t' + valorpr[:just].ljust(just)
            else:
                texto = texto + '\t' + str(stvalor).ljust(just)
        if cabeceras:
            texto += '\n'.ljust(100, '-')
        return texto

    def __str__(self):
        texto = 'ParNombres: {}    {}' \
            .format(self.buscada, self.candidata)
        for nombre in self._medkeys:
            texto = texto + '\n\t' + nombre + '\t' + str(getattr(self, nombre))
        return texto


class EstructuraSolucion(ParNombres):
    def __init__(self, ParNombre):
        self.elementos = []
        self.medidas = []
        # TODO : COMPLETAR ESTO EstructuraSolucion.a


class CorrectorFicheros:
    """
    Encapsulacion para los algoritmos y estructuras para la correcion
        de los nombres de ficheros.
    Se indican como abstractos métodos crearmedidas, filtrar, ordenar y
    crearsolucion, para recalcar que pueden reimplementarse con otros criterios

    corrige->
        CrearMedidas ->
        Ordenar ->
        Filtrar ->
        ObtenerTuplaSolucion->

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, buscadas, candidatas, suptrivial=False):
        """

        :param buscadas: Iterable de str, nombres de ficheros esperados.
        :param candidatas: ..., nombres de ficheros reales.
        :param suptrivial: Indica si se omiten las soluciones triviales.
        :return:
        """
        # COMPROBACIONES
        if not (isinstance(buscadas, collections.Iterable) and
                isinstance(candidatas, collections.Iterable)):
            raise Exception('buscadas y candidatas deben ser un iterable')
        if not buscadas or not isinstance(next(iter(buscadas)), str):
            raise Exception('buscadas debe contener elementos str')
        if not candidatas or not isinstance(next(iter(candidatas)), str):
            raise Exception('candidatas debe contener elementos str')

        # INICIALIZAMOS ATRIBUTOS
        self.buscadas = set(buscadas)
        self.candidatas = set(candidatas)
        self.suptrivial = suptrivial
        # self.pares_medidas = []
        self.pares_aceptados = []
        self.pares_rechazados = []

    def corrige(self):
        """Empareja nombres de los conjuntos buscadas y candidatas, si cumplen
            unos umbrales mínimos de semejanza, basados la distancia de
            levenshtein y coeficientes de correlación (calculados según
            diferentes funciones valor de los caracteres de las cadenas y de
            relleno hasta igualar longitud).

        """
        if not self.buscadas or not self.candidatas:
            return []

        """
        Fragmento para sacar las soluciones triviales, si suptrivial=False,
        que se incluyen en la solucion self.asignaciones y sacar los str
        de self.buscadas y self.candidatas

        self.asignaciones = []

        cjbuscadas = self.buscadas.copy()
        cjcandidatas = self.candidatas.copy()

        sol = set()  # Inicializa el conjunto solucion
        # Se apuntan las soluciones triviales y se quitan de los conjuntos.
        if not self.suptrivial:
            [sol.add((b, c)) for c in cjcandidatas for b in cjbuscadas if
             b == c]
            for b in cjbuscadas.copy():
                for c in cjcandidatas.copy():
                    if b == c:
                        sol.add((b, c))
                        cjbuscadas.remove(b)
                        cjcandidatas.remove(c)
                        self.asignaciones.append( (b, c))
        self.buscadas.clear()
        self.buscadas.extend(cjbuscadas)
        self.candidatas.clear()
        self.candidatas.extend(cjcandidatas)
        self.asignaciones
        """

        # Creación de las medidas implementadas en el método, y filtrado.
        self.crearmedidas()
        medidas = self.pares_aceptados
        rechazos = self.pares_rechazados  # No cumplieron filtros

        # Ordenar e imprimir tuplas.
        if medidas:
            medidas_ord = sorted(medidas, key=lambda pn: pn._clave())
            print(medidas[0]._reprRow(True))  # Para depurar, las cabeceras.
            for pn in medidas_ord:
                print(pn._reprRow())
        print('#'.ljust(100, '#'))
        if rechazos:
            rechazos_ord = sorted(rechazos, key=lambda pn: pn._clave())
            print(rechazos[0]._reprRow(True))  # Para depurar, las cabeceras.
            for pn in rechazos_ord:
                print(pn._reprRow())

        # A continuacion, se obtiene el conjunto de pares compatibles entre
        # si más optimo según los criterios de cota y resultado.
        # Selección de la combinación entre las soluciones.
        # construirsolucion(pares_ord, sol)
        # crearsolucion(medidas_ord)

    @abc.abstractmethod
    def crearmedidas(self):
        """
        Metodo publico abstracto.
        :return:
        """
        self.__crearmedidas()

    @abc.abstractmethod
    def filtrar(self):
        """
        Clasifica pares_aceptados en pares_medidas y pares_rechazados.
        Comparten las referencias de ParNombre
        :return:
        """
        self.__filtrar()

    @abc.abstractmethod
    def ordenar(self):
        self.__ordenar()

    @abc.abstractmethod
    def obtenersolucion(self):
        self.__obtenersolucion()

    def __crearmedidas(self):
        """
        Puebla self.aceptadas y self.rechazadas según las mediciones y filtros
        que empleemos en este metodo para las combinaciones de pares
        entre self.buscadas y self.candidatas:
        A self.pares_medidas una lista con ParNombre y los
        :return:
        """
        cjbuscadas = self.buscadas.copy()
        cjcandidatas = self.candidatas.copy()

        # Funciones para padear nombres y asignar un valor a un carácter.
        def mean_fun(w: str) -> float:
            return sum(w) / len(w)

        def val_b100(ch: str) -> float:
            return valueDist(ch, 1000)

        #  Constantes para el calculo del umbral.
        k1 = 100
        c1 = 1
        refcorr = 2 / 3  # coloca el k1*1 de corrlog a esa corr [0,1]
        cutlev = 1 / 4  # Proporcion sobre la min(len(str)) del par de nombres

        """
        sol = set()  # Inicializa el conjunto solucion
        # Se apuntan las soluciones triviales y se quitan de los conjuntos.
        if not self.suptrivial:
            [sol.add((b, c)) for c in cjcandidatas for b in cjbuscadas if
             b == c]
            for b in cjbuscadas.copy():
                for c in cjcandidatas.copy():
                    if b == c:
                        sol.add((b, c))
                        cjbuscadas.remove(b)
                        cjcandidatas.remove(c)
        """

        medidas = []  # Lista de ParNombre
        rechazos = []

        for busc in cjbuscadas:
            for cand in cjcandidatas:
                # Si la trivial no interesa, saltamos el caso.
                if self.suptrivial and busc == cand:
                    continue

                # Optimización: si tenemos un par y su reflexiva, duplicar el
                # par con sus nombres cambiados en la lista de medidas/rechazos
                # ... continue

                longmax = max(1, max(len(cand), len(busc)))
                umbral = c1 * k1 * k1 * (-log10(1 - cutlev))

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
                measure2 = 1000 * correlacion * (ldist / longmax)

                # Nuevo PN con medidas introducidas. nuevoorden para prioridad.
                objmedidas = ParNombres(busc, cand,
                                        levdis=ldist,
                                        ord_0_corr=e, spa_0_corr=f,
                                        ord_mean_corr=g, spa_mean_corr=h,
                                        max_corr=correlacion, lev_log=levlog,
                                        corr_log=corrlog,
                                        measure=measure)
                objmedidas.nuevoorden('buscada', 'candidata', 'levdis',
                                      'measure')

                # Agregar a candidatas si cumple las condiciones mínimas.
                if (measure < umbral) or (correlacion >= refcorr) or \
                        (ldist < ceil(cutlev * min(len(busc), len(cand))) + 1):
                    medidas.append(objmedidas)  # medidatup)
                else:
                    rechazos.append(objmedidas)  # medidatup)
        self.pares_aceptados = medidas
        self.pares_rechazados = rechazos
        return True

    def __filtrar(self):
        pass

    def __ordenar(self):
        pass

    def __obtenersolucion(self):
        """
        Algoritmo recursivo de ramificación y poda, con poda basada en una
        función objetivo

        Hay que considerar el caso de soluciones parciales y totales.
        :return:
        """
        longitudes = [len(x) for x in self.buscadas]
        mejordistancia = max(longitudes) - min(longitudes)
        for v1 in self.buscadas:
            for v2 in self.buscadas:
                if v1 == v2:
                    break
                distancia = d_levenshtein(v1, v2)
                if distancia >= mejordistancia:
                    break

    def __solrecursiva(self, tuplasol, grupos, it=0):
        pass

if __name__ == "__main__":

    def test_subsWords():
        """
        Testeo de la funcionalidad de filecorrector.
        """
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


        # Llamamos los métodos de CorrectorFicheros
        corregidor = CorrectorFicheros(palas, palas, suptrivial=True)
        tupla = corregidor.corrige()
        for name1, name2 in tupla:
            print(name1, '->', name2)

    test_subsWords()


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