#!/usr/bin/env python3
# encoding: utf-8
"""
PyfichAnaly -- shortdesc
PyfichAnaly is a description
It defines classes_and_methods
@author:     user_name
@copyright:  2014 organization_name. All rights reserved.
@license:    license
@contact:    user_email
@deffield    updated: Updated
"""

import json
import os
# Interfaz de transición de flake8 v2 hasta que publiquen la api publica de v3.3
# TODO Actualizar el código con la api de la v3 de flake8 cuando se publique
import os.path as op
import subprocess

from pylint import epylint as lint

from entities.student import Student


def analy_code(stud_obj: Student, pyfiles: list) -> dict:
    """
    Script de análisis pep8 y pilint, síntesis en diccionario e impresión.
    """
    pypaths = [os.path.join(stud_obj.gitPath, x) for x in pyfiles]
    data = dict()
    data['pep8'] = Pep8An(pypaths, stud_obj)
    data['pylint'] = PylintAn(pypaths, stud_obj)
    
    # REPRESENTACION DE RESULTADOS en txt de salida legibles.
    #stud_obj.writeResultStud(str(data['pep8']) + '\n')# + str(data['pylint']))
    #stud_obj.writeResultTeach(
        #data['pep8'].__str__() + '\n')  # +
        #data['pylint'].__str__(PylintAn.RATING, PylintAn.PYLINT_ERRORS))
    print(data['pep8'].__str__() + '\n'   +
        data['pylint'].__str__(PylintAn.RATING, PylintAn.PYLINT_ERRORS))
    
    return data


class PylintError:
    def __init__(self, **args):
        self._attrlist = []
        for k, v in args.items():
            setattr(self, k, v)
            self._attrlist.append(k)
    
    def getattrnames(self):
        return self._attrlist.copy()
    
    def __str__(self):
        ret = 'PylintError class with attr\n'
        for k in self._attrlist:
            ret += '\t{}\t{}\n'.format(k, getattr(self, k))
        return ret
    

class PylintAn:
    RATING = 'rating'
    PYLINT_ERRORS = 'errors'
    KEYS_TAGS = ((RATING, 'Pylint rating'),
                 (PYLINT_ERRORS, 'Pylint errors'))
    TMP_PYL = 'pylinttmp.txt'

    def __init__(self, pypaths: list, stud_obj: Student):
        # Ejecucion pylint. stdout a tmppyl y errs a ficheros de stud/teach
        cmd = 'pylint --disable=C0111,C0103,W0231,W0232,W0621,F0401 {} ' \
            '2>&1 1> {} | tee -a {} {} >/dev/null'.format(' '.join(pypaths),
                                                          self.TMP_PYL,
                                                          stud_obj.errorPath,
                                                          stud_obj.teachPath)
        (status, output) = subprocess.getstatusoutput(cmd)
        print(status)
        print(output)
        # Analisis de ficheros y empaquetado en un diccionario
        res_dict = self._analy_pylint(self.TMP_PYL)
        self.results = res_dict
        for k, v in res_dict.items():
            print(k, v)

    def _analy_pylint(self, rpath: str) -> dict:
        pylint_errors_list = []
        pylint_rating = ""
        fd = open(rpath)  # Default: r
        while 1:
            line = fd.readline()
            if not line:
                break
            print(line)
            if line[0] in ['*', 'C', 'W']:
                pylint_errors_list.append(line[:-1])
            elif 'Your code has been rated at ' in line:
                pylint_rating = line.split()[6]
        try:
            mark_pylint_rating = float(pylint_rating.split('/')[0])
        except ValueError:
            mark_pylint_rating = 0
        fd.close()
        """
        output = open('detalles/prac2-' + alumno, 'w')
            for line in pylint_errors_list:
            output.write(line + '\n')
        output.write('\n')
        output.close()
        """
        data = {self.RATING: [mark_pylint_rating],
                self.PYLINT_ERRORS: pylint_errors_list}
        return data
        
    @staticmethod
    def __dict_obj(dic):
        # Funcion que usaremos para interpretar el dict leido para este Json
        # Se espera solo claves-valores str/int sin nuevas [] {} anidadas.
        args = dic.copy()
        ret = PylintError(**args)
        return ret
        
    @staticmethod
    def analy_pylint_msgs(base, filelist, errdis):
        """
        Obtener listado de errores pylint dadas rutas de ficheros python.
        Se llama desde la libreria en Python y elegimos json como salida.
        :param filelist: Listado de path de ficheros py a analizar
        :param errdis: str de códigos de error a ignorar separados por comas.
        :return:
        """
        # TODO INTRODUCIR COMPROBACION DE LA LISTA DE RUTAS DE FICHEROS PY

        rutas = []
        for x in filelist:
            ruta = op.normpath(op.join(op.normpath(base), op.normpath(x)))
            rutas.append(ruta)
        files = '\t'.join(rutas)
        
        # Se llama pylint con py_run de la libreria pylint en python.
        # return_std=True redirecciona stdout y no la imprime.
        (pyout, pyerr) = lint.py_run(
            '{files} --output-format=json --persistent=n --disable={disable} '
                .format(files=files, disable=errdis), return_std=True)

        err = pyerr.readlines()
        # Para seguir, no errores o sólo el warning de no uso de fichero config.
        if not (len(err) == 0 or (len(err) == 1 and err[0] ==
            'No config file found, using default configuration\n')):
            raise Exception('Ejecucion de pylint con errores')

        # Cargamos el stream con json. __dict_obj interpretamos los {}
        result = json.load(fp=pyout, object_hook=PylintAn.__dict_obj)
        
        # Listado de objetos PylintError con su información.
        return result

        
    def __str__(self, *str_keys):
        """
        Método de str con opción de elegir con strkeys que imprimimos.
        """
        str_keys_ = str_keys if str_keys else self.results.keys()
        outp = '\n######## RESULTADOS DE PYLINT ###########\n'
        for key in str_keys_:
            for key_tag, tag in self.KEYS_TAGS:
                if key_tag == key:
                    outp += '\n' + tag + ':\n'
                    for el in self.results[key_tag]:
                        outp += '\t' + str(el) + '\n'
                #else:
                #    mutils.addErrorToFiles("{}.__str__: key {} isn't in "
                #                           .format("self.results"))
        # os.remove Pep8An.TMP_STATS, Pep8An.TMP_SRC, PylintAn.TMP_PYL
        return outp


class Pep8An:
    """
    Clase con funcionalidad básica para analizar un conjunto de ficheros
    python con pep8 y a partir de la salida de texto almacenarla en
    estructuras.
    """
    NUM = 'numerrors'
    STATS = 'stats'
    SOURCES = 'sources'
    KEYS_TAGS = ((NUM, 'Número de errores pep8'),
                 (STATS, 'Resumen de estadísticas pep8'),
                 (SOURCES, 'Errores pep8 encontrados'))
    TMP_SRC = 'peptmpsources.txt'
    TMP_STATS = 'peptmpstats.txt'

    def __init__(self, pypaths: list, stud_obj: Student, ignore: str = ''):
        """
        Análisis de la salida de shell pep8 y pilint
        MEJORAR: usar librerias pep8 y pilint directas en python.
        """
        SRCPATH = stud_obj.username + '-' + self.TMP_SRC #'tmptmp/' +
        STATPATH = stud_obj.username + '-' + self.TMP_STATS #'tmptmp/' +
        # Ejecutamos 2 pep8, para stud y teach, resultados a tmps, err a files.
        """cmd_source = 'pep8 --repeat --show-source {} > {} 2>> {}' \
            .format(' '.join(pypaths), SRCPATH, stud_obj.errorPath)
        (status1, output1) = subprocess.getstatusoutput(cmd_source)
        cmd_stat = 'pep8 -q --statistics {} > {} 2>> {}' \
            .format(' '.join(pypaths), STATPATH, stud_obj.teachPath)
        (status2, output2) = subprocess.getstatusoutput(cmd_stat)"""
        if os.path.isfile(SRCPATH):
            os.remove(SRCPATH)
        if os.path.isfile(STATPATH):
            os.remove(STATPATH)
        

        cmd_source = 'pep8 --repeat --show-source {} > {}' \
            .format(' '.join(pypaths), SRCPATH)
        (status1, output1) = subprocess.getstatusoutput(cmd_source)
        cmd_stat = 'pep8 -q --statistics {} > {}' \
            .format(' '.join(pypaths), STATPATH)
        (status2, output2) = subprocess.getstatusoutput(cmd_stat)
        
        # Status de pep8 0 si la salida es nula. 1
        # 1 si tiene algo (aunque sea erronea)
        #print(status1, status2)
        #print(output1, output2, status1, status2)
        #subprocess.getstatusoutput('gedit {} {} &'.format(
        #    SRCPATH, STATPATH))
        #if str(status1) != '0' or str(status2) != '0':
        #    subprocess.getstatusoutput('gedit {} &'.format(
        #        stud_obj.errorPath))
        #    print('abierto gedit')
        # Analisis de ficheros y empaquetado en un diccionario
        pep8dict = self._analy_pep8(SRCPATH, STATPATH)
        self.results = pep8dict

    def _analy_pep8(self, sources_rpath: str, stats_rpath: str) -> dict:
        """
        Análisis del volcado de pep8 a los ficheros
        :param sources_rpath: ruta de volcado de pep8 con --show-sources
        :param stats_rpath: ruta de volcado de pep8 con --statistics
        :return: diccionario con la estadísticas pep8 extraidas
        """
        pep8_errors = 0
        pep8_stats_list = []
        pep8_errors_sources = []
        # Extraemos el detalle de cada error pep8
        fd = open(sources_rpath, 'r')
        while 1:
            line = fd.readline()
            if not line:
                break
            pep8_errors_sources.append(line[:-1])
        fd.close()
        # Extraemos las estad. de cada tipo de error.
        fd = open(stats_rpath, 'r')
        while 1:
            line = fd.readline()
            if not line:
                break
            pep8_stats_list.append(line[:-1])
            # words = line.split()
            try:
                pep8_errors += int(line.split()[0])
            except IndexError:
                pass
            except ValueError:
                pass
        fd.close()
        data = {self.NUM: [pep8_errors],
                self.STATS: pep8_stats_list,
                self.SOURCES: pep8_errors_sources}
        return data
    
    @staticmethod
    def pep8py(ruta, ficheros):
        """
        Analisis pep8 desde la propia libreria instalada en python.
        :return:
        """

    def __str__(self, *str_keys):
        """
        Método de str con opción de elegir con strkeys que imprimimos.
        """
        str_keys_ = str_keys if str_keys else self.results.keys()
        outp = '\n######## RESULTADOS DE PEP8 ###########\n'
        for key in str_keys_:
            for key_tag, tag in self.KEYS_TAGS:
                if key == key_tag:
                    outp += '\n@@@@@@@@@@ ' + tag + ' @@@@@@@@@@@:\n'
                    for el in self.results[key_tag]:
                        outp += '\t' + str(el) + '\n'
                #else:
                #    mutils.addErrorToFiles("{}.__str__: key {} isn't in "
                #                           .format(__name__))
        return outp


class Flake8Analy:
    
    def __init__(self):
        pass
    
    @staticmethod
    def flake_run(path, disable):
        pass

    def __api_publica_flake8(self):
        # ESTA LA API DE V3 INCOMPLETA TODAVIA
        # import flake8
        import flake8.api.legacy as flake8
        # De momento
        # H233 Y E999 los quitamos ya que dan falsos positivos corrigiendo python 2.
        disable = 'E502,E125,E127,E128,C0103,W0231,W0621,H233,E999'
        style_guide = flake8.get_style_guide(
            # ignore=disable.split(','),
            # statistics=True
        )
        # report = style_guide.check_files([ruta])
        # assert report.get_statistics('E') == [], 'Flake8 found violations'
        # print('Total ', report.total_errors)
        # Esta api por ahora devuelve la estadistica  count codigo texto en lineas.
        '''
        for k in ['E','C', 'H', 'W', 'F','R']:
            st = report.get_statistics(k)
            for x in st:
                print(x)
        '''
        # print(report.get_statistics(, report.total_errors())
        # pep8.StyleGuide
        

if __name__ == "__main__":
    '''
    ruta = '/home/chilli-mint/tmp/misture/4143544956494441445f4341/github/opedraza/'
    
    
    # Prueba de pep8 y pylint con llamada a bash y parseo del texto de fichero.
    class Pc:
        errorPath = 'errorPath.txt'
        teachPath = 'teachPath.txt'
        username = 'usuario'

    pyl = PylintAn(['CodeAnaly.py'], Pc)
    p8 = Pep8An(['CodeAnaly.py'], Pc)

    for k, v in pyl.results.items():
        print(k)
        for el in v:
            print(v)
    [print() for x in range(10)]
    for ky, val in p8.results.items():
        print(ky)
        for el in val:
            print(val)
    '''

    '''
    # Prueba de Pylint con py_run y carga desde stringIO de json generado
    # con los errores detectados.
    # Pylint cambia el path a relativo si comparte con el path que lo invoca.
    files = \
        '/home/chilli-mint/Desktop/PFC_LAST/00_pruebas_aisladas/const.py ' \
        '/home/chilli-mint/Desktop/PFC_LAST/00_pruebas_aisladas/subdir/mailing.py ' \
        '/home/chilli-mint/tmp/misture/4143544956494441445f4341/github/opedraza/client.py '
    errores = PylintAn.analy_pylint_msgs(files, 'E125,E127,E128')
    for e in errores:
        print(e)


    # PEP8 DESDE PYTHON IMPRIME LOS ERRORES INDIVIDUALES POR PANTALLA,
    # SOLO SERVIRIA PARA OBTENER LA INFORMACIÓN AGREGADA.
    import pylint
    import pep8
    print('StyleGuide')
    p8s = pep8.StyleGuide(quiet=True)
    print('CHeck files or dir')
    result = p8s.check_files(['/home/chilli-mint/Desktop/PFC_LAST/00_pruebas_aisladas/const.py',
        '/home/chilli-mint/Desktop/PFC_LAST/00_pruebas_aisladas/llamarPylint.py'])
    #result = p8s.input_dir('/home/chilli-mint/Desktop/PFC_LAST/00_pruebas_aisladas/')
    print(type(result))
    
    if result is not None:
        print('\n>>', result.get_file_results(), result.file_errors, result.get_count(), '\n\n>>',
            type(result.get_statistics()), result.get_statistics(), '\n\n>>',
        )
        print('####################################')
        result.print_statistics()
        print('####################################')
        result.print_benchmark()
        print(result)
        print('####################################')
        print()
    '''
    
    
    