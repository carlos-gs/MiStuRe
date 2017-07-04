#! /usr/bin/python3
# encoding: utf-8
import subprocess
import sys

import entities.mongops

#entities.mongops.borrarindicesevitardups()
#entities.mongops.borrardb()

import pymodm
# from pymongo import MongoClient
# MongoClient().drop_database('misture_mbbd')
#pymodm.connect('mongodb://localhost:27017/misture_mbbd')
from entities.pymdbodm import *

(major, minor, release, status, revision) = sys.version_info

from entities.pymdbodm import DirectoriosActividad

"""
TODO OJO: sloccount es problematico con las rutas. La solución menos mala
seria intentar calcular la ruta absoluta para pasarla como parametro de
sloccount y en la salida la columna de path debemos eliminar la ruta hasta
llegar a la raiz del proyecto con sus ficheros y subdirectorios. Si pasamos
como parametro un path relativo, el path de salida hasta el proyecto es el
mismo del parametro aunque sea relativo o tenga ../ ./ o links.
"""


# Ruta temporal donde se lanza pylint para el repositorio analizado
# ruta_base = '/home/chilli-mint/Desktop/PFC_LAST/00_pruebas_aisladas/'
# Se debera componer dinamicamente unas rutas absolutas donde
# se ubican temporalmente los .py en el repositorio.
# files = 'const.py subdir/mailing.py'
# Donde guardo la salida del analisis pylint
# ruta_salida=ruta_base
# fichero_salida='salida_carlos.json'

class Slocfichero:
    """
    Clase auxiliar para el almacenamiento de resultados de un simple
    analisis sloc para un fichero dentro de un directorio-proyecto.
    """
    
    def __init__(self, rutarel, sloc, lenguaje):
        """
        
        :param rutarel: ruta relativa dle fichero dentro del dir-proyecto
        :param sloc: número de líneas sloc
        :param lenguaje: lenguaje que ha identificado sloccount en el fichero
        """
        try:
            self.ruta = rutarel
            self.sloccount = int(sloc)
            self.lenguaje = lenguaje
        except:
            raise
    
    def __str__(self):
        return 'Slocfichero: {} en el lenguaje {} con {} líneas'.format(
            self.ruta, self.lenguaje, self.sloccount)
    

class Sloccount:
    __COM_PARAM_LINUX = """ \
sloccount --details --follow --duplicates {} | grep -P \
'^\d+\t' | sed 's/\t/:/g' """
# | awk '{{print $1 ":" $2 ":" $4}}'

    def __init__(self, ruta, actividad='', usuario=''):
        self.ruta = os.path.abspath(ruta)
        self.slocs_listado = []
        self.__ejecutar_sloc()
    
    def __resolver_comando(self):
        """
        Se resuelve el comando linux parametrizado indicado en __COM_PARAM_LINUX
        :return: str con el comando que se deseará ejecutar
        """
        return self.__COM_PARAM_LINUX.format(self.ruta, re.escape(self.ruta))
    
    def __ejecutar_sloc(self):
        """
        Se ejecuta y almacena los resultados de la ejecución del comando
        parametrizado que realiza el pequeño análisis de sloccount sobre
        los ficheros de un directorio/proyecto indicado en la ruta.
        :return:
        """
        self.slocs_listado.clear()
        (status, out) = subprocess.getstatusoutput(self.__resolver_comando())
        # Procesado de la salida del comando.
        if int(status) == 0:
            for linea in out.split('\n'):
                if linea.strip() == '':
                    continue
                elems = linea.split(':')
                if len(elems) != 4:
                    print('Sloccount.__ejecutar_sloc leida línea inesperada {}'
                          .format(linea))
                    continue
                (sloc, lang, rel_dir, path_fichero) = elems
                ruta_pwd = os.getcwd()
                ruta_par = self.ruta
                ruta_fichero = path_fichero
                # Extraemos del path de cada codigo la ruta relativa del
                # proyecto.
                # sloccount imprime como path_fichero
                # ruta_parametro+ruta_rel_cod
                # si es absoluta o pwd+ruta_parametro_rel+ruta_rel_cod si
                # relativa
                # Procesamos las casuisticas para obtener solo la ruta_rel_cod
                if ruta_par.find(ruta_pwd + '/') == 0:
                    ruta_fichero = ruta_fichero[len(ruta_pwd) + 1:]
                else:
                    if ruta_fichero.find(ruta_pwd + '/') == 0:
                        ruta_fichero = ruta_fichero[len(ruta_pwd) + 1:]
                    if ruta_fichero.find(ruta_par + '/') == 0:
                        ruta_fichero = ruta_fichero[len(ruta_par) + 1:]
                # Construimos el objeto que almacena resultado y a una lista.
                sloc_res = Slocfichero(ruta_fichero, sloc, lang)
                self.slocs_listado.append(sloc_res)
        else:
            raise Exception('Sloccount erroneo para ruta ' + self.ruta)
    
    def get_slocanaly(self):
        return self.slocs_listado
        
    def __str__(self):
        cadena = ''
        for sloc in self.slocs_listado:
            cadena = cadena + str(sloc) + '\n'
        return cadena






'''class ClasificadorPr:
    
    def __init__(self, rutabs, rutarel=''):
        self.rutabs = rutabs
        self.rutarel = rutarel
        self._udfiles = {}
        self._udorder = []'''

def identificarfichero(rel, base):

    relpath = DirectoriosActividad.unir(rel,base)
    
    # Generar udfile. TIPO_FILE si no se infiere otra cosa.
    udf = Udfile(pathrel=relpath, nombre=base, tipo=Udfile.TIPO_FILE)
    
    # Identificar la extension
    text1 = op.splitext(base)
    text2 = op.splitext(text1[0])
    ext = text2[1] + text1[1]
    # Identificar tipo para ponerle bien el tipo.
    if ext.lower() in ('.xml', '.pdml', '.smil'):
        udf.tipo = udf.TIPO_XML
    elif ext.lower() in ('.libpcap', '.pcapng', '.libpcap.pcapng', '.libpcap'):
        udf.tipo = udf.TIPO_LIBPCAP
    #print(base, '\t', rel, ext, '\t', udf.tipo, text2[1] , text1[1])
    # TIPO_SRC y lenguaje SE MARCARA EN OTRO PROC A TRAVES DE SLOCCOUNT
    # pass

    return udf


def obtenerestructura(ruta):
    """
    Analisis de los ficheros presentes en un directorio absoluto.
    :param ruta: path de unix con la ruta a analizar
    :return:
    """
    if not (os.path.isabs(ruta) and os.path.isdir(ruta)):
        # raise Exception\
        print('obtenerestructura: se espera un dir existe en ' +
              'path abs en lugar de ' + ruta)
        
    # Para disponer los Udfiles referenciados por pathrel y ordenados.
    udfiles = {}
    udorder = []

    for dirpath, dirnames, filenames in os.walk(ruta):
        # /dir_repo/relpath  relpath-> . o subdir1/subdirbase o subdir1/fich.txt
        relpath = op.relpath(dirpath, ruta)
        dirnm = op.dirname(op.normpath(relpath))
        basen = op.basename(op.normpath(relpath))
        if dirnm == '':
            dirnm = '.'
        if basen == '':
            basen = '.'
        
        if relpath in ('.', ''):
            dirbd = Udfile(pathrel='.', nombre='.', tipo=Udfile.TIPO_RAIZ)
        elif re.search('(/\.git/)|(^\.git/)', relpath):
            dirbd = None
            continue  # TODO IGNORAMOS. Saltamos sig it
        elif basen == '.git':
            dirbd = Udfile(pathrel=relpath, nombre='.git', tipo=Udfile.TIPO_GIT)
        else:
            dirbd = Udfile(pathrel=relpath, nombre=basen, tipo=Udfile.TIPO_DIR)
        
        # Almacenamos en dicc y list
        if dirbd:
            udfiles[dirbd.pathrel] = dirbd
            udorder.append(dirbd)
        # Buscamos al padre ya instanc. y se agrega este hijo.
        if relpath != '.':
            hijos = udfiles[dirnm].hijos
            hijos.append(dirbd)
            udfiles[dirnm].hijos = hijos
            # TODO aqui deberia manejarse si fallan [] por nokey o str vacio
        
        # Navegamos entre los filenames
        udflnms = []
        for fich in filenames:
            udf = identificarfichero(relpath, fich)
            # Registramos el Udfile en el dic y lis
            udfiles[udf.pathrel] = udf  # TODO quizas manejar nokey o error
            udflnms.append(udf)
            udorder.append(udf)
    
        # Asociamos todos los hijos con sus Udfiles ya creados.
        hijos = udfiles[dirbd.pathrel].hijos
        hijos.extend(udflnms)
        udfiles[dirbd.pathrel].hijos = hijos
        
    # SLOCCOUNT Del analisis obtenemos la rutarel para reasocialos a los objetos.
    slocanaly = Sloccount(ruta)
    slocs = slocanaly.get_slocanaly()
    for fichsloc in slocs:
        
        srcrelpath = fichsloc.ruta
        if op.dirname(srcrelpath) == '':
            srcrelpath = op.join(os.curdir, srcrelpath)
        try:
            # Sacamos el registro del dicc, añadimos/editamos su info.
            udfsrc = udfiles[srcrelpath]
            udfsrc.lenguaje = fichsloc.lenguaje
            udfsrc.sloc = fichsloc.sloccount
            udfsrc.tipo = Udfile.TIPO_SRC
            #ud2 = udfsrc.save()
        except KeyError:
            LogError.guardarerrorlog('En ' + ruta + ' hay un src ' +
                srcrelpath + ' que no almacenaremos y hierra al buscar. ',
                accion='si es .git, nada, proseguir.')
        except:
            raise
    # DEvolvemos la lista de objetos en el orden en que deben ser guardados.
    return udorder
    # Guardo en lote en bd en orden inverso de insercción (por los ReferenceF.)
    # ids = Udfile.objects.bulk_create([udf for udf in reversed(udorder)])
    

if __name__ == "__main__":
    pass

