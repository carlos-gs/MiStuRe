#!/usr/bin/env python3
# encoding: utf-8

print('IMPORTANDO MODELO DE DATOS...')

import datetime
import os
import os.path as op
import re
import shutil

import validators  # Añadir algún validador adicional
# Elementos del ODM pymdom
from pymodm import *
from pymodm.errors import *
from pymodm.fields import ReferenceField as Rf
# Algunos elementos deben usarse directamente de pymongo
from pymongo import IndexModel, ASCENDING, TEXT

# PATRONES REGULARES YA COMPILADOS
from settings.patrones import *


# Patron para validar una ruta de linux.

# import time


# Borro la base las colecciones e indices con nuestro metodo personalizado
# import entity_mongo.mongops
# entity_mongo.mongops.borrarindicesevitardups()
# entity_mongo.mongops.borrardb()



# El alias por defecto en connect es default. Si se cambia, añadir en los Meta.
# misture_db_alias = 'misture'
# Llamada a la conexión a MongoDB desde pymodm.connect antes de los modelos.
# PARA PODER USAR EN DJANGO ESTE MODULO, NO HACEMOS AQUI LA CONEXION
# connect('mongodb://localhost:27017/' + Cg.MONGODB)
# connect('mongodb://localhost:27017/prueba_bbdd')  # , alias=misture_db_alias)


class LogError(MongoModel):
    descripcion = CharField()
    accion = CharField()  # Descripcion acción (nada, abortar, borrar regs)
    traza = CharField()
    fecha = DateTimeField(default=datetime.datetime.now())
    actividad = ReferenceField('Actividad', blank=True)
    correccion = ReferenceField('Correccion', blank=True)
    
    @staticmethod
    def guardarerrorlog(descripcion, accion=None, traza=None,
                        actividad=None, correccion=None, **kargs):
        le = LogError(descripcion=descripcion, accion=accion, **kargs)
        le = le.save()
        return le


class UsuarioMisture(MongoModel):
    ROL_CORRECTOR = 'ADM'
    ROL_DESARROLLADOR = 'ALU'
    ROLES_MISTURE = ((ROL_CORRECTOR, 'CORRECTOR'),
                     (ROL_DESARROLLADOR, 'DESARROLLADOR'))
    login = CharField(primary_key=True, min_length=4, max_length=50)
    email = EmailField() #required=True)
    rol = CharField(choices=ROLES_MISTURE)
    date = TimestampField(default=datetime.datetime.now())
    
    def clean(self):
        """
        Hago validaciones propias y elevo ValidationError si no es valido
        """
        pass
    
    def __str__(self):
        return self.__class__.__name__ + " " + self.login.__str__()
        
        # class Meta:
        #     connection_alias = misture_db_alias


class Corrector(UsuarioMisture):
    # todo La herencia no funciona al recuperar los atributos que se heredan
    # Aunque si funcionan al instanciar y guardar.
    # Los hemos duplicado de momento hasta encontrar la solución.
    login = CharField(primary_key=True, min_length=4, max_length=50)
    email = EmailField() #required=True)
    actividades = ListField(ReferenceField('Actividad'), default=[])
    rol = CharField(choices=(
        (UsuarioMisture.ROL_CORRECTOR, 'CORRECTOR')),
        default=UsuarioMisture.ROL_CORRECTOR
    )
    superrol = BooleanField(default=True)


class Desarrollador(UsuarioMisture):
    # todo La herencia no funciona al recuperar los atributos que se heredan
    # Aunque si funcionan al instanciar y guardar.
    # Los hemos duplicado de momento hasta encontrar la solución.
    login = CharField(primary_key=True, min_length=4, max_length=50)
    email = EmailField() #required=True)
    emails = ListField(EmailField(), mongo_name='emails_alt', default=[])
    rol = CharField(choices=(
        (UsuarioMisture.ROL_DESARROLLADOR, 'DESARROLLADOR')),
        default=UsuarioMisture.ROL_DESARROLLADOR
    )
    date = TimestampField(default=datetime.datetime.now())


class DirectoriosActividad(EmbeddedMongoModel):
    PBASE=1
    PENTREGA=2
    PREPOTMP=3
    PREPOEJEC=4
    PTEST=5
    PRESULTADOS=6
    PERRORES=7
    PPRUEBAS=8
    PPROFESOR=9
    pbase = CharField(default='/tmp/misture/actividad/')
    pentrega = CharField(default='entrega/')  # destino del volcado
    prepo_tmp = CharField(default='repo_tmp/')  # copia volcado para checks
    prepo_ejec = CharField(default='repo_ejec/')  # copia volcado para copiar ficheros prueba y ejecutar test
    ptest = CharField(default='test/')
    presultados = CharField(default='resultados/')
    perrores = CharField(default='errores/')
    
    ppruebas = CharField(default='/tmp/misture/')
    # Este directorio no se crea, es solo input
    pprofesor = CharField()  # Este no se borra

    
    def __str__(self):
        return __class__.__name__ + '\n' + \
               '\t' + self.pbase + self.pentrega + '\n' + \
               '\t' + self.pbase + self.presultados + '\n' + \
               '\t' + self.pbase + self.perrores + '\n' + \
               '\t' + self.pbase + self.ptest + '\n'
    
    def rutapara(self, tipo_ruta):
        casos = {1: self.pbase, 2: self.pentrega, 3: self.prepo_tmp,
                 4: self.prepo_ejec, 5: self.ptest, 6: self.presultados,
                 7: self.perrores, 8: self.ppruebas, 9: self.pprofesor}
        if not (isinstance(tipo_ruta, int) and 1 <= tipo_ruta <= 9):
            raise Exception('DirectoriosActividad.rutapara tipo_ruta no valida')
        ruta = casos[tipo_ruta]
        if op.isabs(ruta):
            return ruta
        rfinal = self.unir(self.pbase, ruta)
        return rfinal
        
        
    
    def rutapara_login(self, tipo_ruta, identificador):
        
        ruta = self.unir(self.rutapara(tipo_ruta), identificador)
        return ruta
    
    def clean(self):
        """
        Validamos pbase como ruta absoluta y las demas como relativas a esta.
        :return: True si no han surgido excepciones
        """
        if not re.match(M_REGEX_PATH, self.pbase):
            raise ValidationError(__class__ + '.pbase no valida ' + self.pbase)
        for rel in [self.pentrega, self.presultados, self.perrores, self.ptest,
                    self.prepo_tmp, self.prepo_ejec]:
            if not re.match(M_REGEX_PATH, self.pbase + rel):
                raise ValidationError(__class__ + 'directorio no valido ' +
                                      self.pbase + rel)
        return True
    
    def creardirectorios(self, paralogines=[]):
        """
        TODO: falta que funcione para cualquier combinacion de rutas
        absolutas con respecto pbase como absolutas como mezcla
        Crea en la computadora los directorios, previamente validados.
        :return: True si no han surgido excepciones
        """
        try:
            self.full_clean()
        except:
            raise
        # Creamos la base y los relativos.
        if not op.isdir(self.pbase):
            os.makedirs(self.pbase)
        # op.isabs()
        for rel in [self.pentrega, self.presultados, self.perrores, self.ptest,
                    self.prepo_tmp, self.prepo_ejec]:
            if not op.isdir(self.unir(self.pbase, rel)):
                os.makedirs(self.unir(self.pbase, rel))
                
        # Creamos subdirectorios con logines si nos dan listado
        for rel in [self.presultados, self.perrores,self.ptest]:
            for log in paralogines:
                subdir = self.unir(self.pbase, rel, log)
                if not op.isdir(subdir):
                    os.makedirs(subdir)
                
        return True
    
    @staticmethod
    def unir(*args):
        args2 = [op.normpath(p) for p in args]
        ruta = args2[0]
        #for p in args2[1:]:
        return op.join(*args2)
    
    
    def borrardirectoriosbase(self):
        """
        Borrar todo el directorio
        :return:
        """
        try:
            self.full_clean()
        except:
            raise
        if op.isdir(self.pbase):
            shutil.rmtree(self.pbase)


'''
class FicherosCorrector(MongoModel):
    """
    Localizacion inicial y rutas relativas de ficheros auxiliares para una
    correccion: ficheros o modulos para ejecutar las pruebas de las
    correcciones,
        preguntas generales de examen, jsones de configuraciones.
    """
    actividad = ReferenceField('Actividad')
    directorio = CharField(default='/tmp/misture/actividad/')
    ficheros = ListField(CharField(default=[]))
'''


class Actividad(MongoModel):
    descripcion = CharField(min_length=7)
    corrector = ReferenceField(Corrector, on_delete=Rf.DENY)
    desarrolladores = ListField(
        ReferenceField(Desarrollador, on_delete=Rf.PULL))
    entregas = ListField(EmbeddedDocumentField('Entrega'), blank=True)
    directorios = EmbeddedDocumentField(DirectoriosActividad, blank=True)
    """
    Recordatorio:
    CONFIGURACION
    RUTAS_VOLCADO -> directorios
    CORRECCIONES
    RUTA_FICHEROS_AUX default=rutafija/<autoid>
    FICHEROS_AUX = [xml serverprueba.py docu.pdf examengenerico.txt]
    """
    
    def __str__(self):
        return '\t'.join([str(x) for x in (__class__.__name__, self._id,
                                           self.corrector.login,
                                           self.descripcion, self.directorios)])
    
    class Meta:
        indexes = [
            IndexModel([('descripcion', TEXT)], name='actdes')
        ]


# Corrector.register_delete_rule(Actividad, 'actividad', Rf.NULLIFY)


class Correccion(MongoModel):
    fecha = DateTimeField(default=datetime.datetime.now())
    actividad = ReferenceField(Actividad, on_delete=Rf.CASCADE)
    desarrollador = ReferenceField(
        Desarrollador)  # , mongo_name='desarrollador_1')
    desarrolladores = ListField(
        ReferenceField(Desarrollador, on_delete=Rf.PULL),
        default=[])
    # estructura
    # metricas
    # codigo
    # output/test
    gitanaly = EmbeddedDocumentField('GitAnaly')
    
    class Meta:
        indexes = [
            IndexModel([('actividad', ASCENDING), ('desarrollador', ASCENDING)],
                       unique=True, name='cor_actfec_pk')
        ]
        ''', ('fecha', ASCENDING)'''


class Entrega(EmbeddedMongoModel):
    TIPO_GITURL = 'GIT_URL'
    TIPO_LOCAL = 'LOCAL_PATH'
    _TIPO_ENTREGA = (
        (TIPO_GITURL, 'REPOSITORIO GIT REMOTO'),
        (TIPO_LOCAL, 'DIRECTORIO EN RUTA LOCAL')
    )
    # actividad = ReferenceField(Actividad, on_delete=Rf.CASCADE)
    desarrollador = ReferenceField(Desarrollador)
    modo = CharField(required=True, choices=_TIPO_ENTREGA)
    ubicacion = CharField()
    correccion = ReferenceField(Correccion, on_delete=Rf.NULLIFY)
    
    def clean(self):
        """
        ubicacion como url o como ruta segun el modo
        :return: True si no han surgido excepciones
        """
        if (self.modo == self.TIPO_LOCAL and not
        re.match(M_REGEX_PATH, self.ubicacion)):
            raise ValidationError(
                __class__.__name__ + '.ubicacion local no valida '
                + self.ubicacion + ' para ' + self.modo)
        elif self.modo == self.TIPO_GITURL:
            try:
                validators.url(self.ubicacion)  # True o ValidationFailure
            except Exception as evf:
                raise ValidationError(
                    __class__.__name__ + '.ubicacion url no valida '
                    + self.ubicacion + ' para ' + self.modo)


class TrazaXML(MongoModel):
    correccion = ReferenceField(Correccion)
    fecha_verif = DateTimeField(default=datetime.datetime.now())
    fichero = CharField()
    #comprobacion = CharField()
    traza = CharField()
    

'''
class Metrica(MongoModel):
    """
    Recoge una estructura aproximada para almacenar el resultado de
    métricas realizadas a nivel de fichero fuente, grupo de ficheros,
    proyecto
    """
    AMBITO_METRICA = (
        ('FILE', 'FICHERO FUENTE DEL PROYECTO'),
        ('DIR', 'FICHEROS FUENTE DE UN SUBDIRECTORIO DEL PROYECTO'),
        ('PROJ', 'FICHEROS FUENTE DEL PROYECTO')
    )
    entrega = ReferenceField(Correccion, on_delete=Rf.CASCADE)
    ambito = CharField(choices=AMBITO_METRICA)
    relpath = CharField(verbose_name='Ruta relativa dentro del proyecto')
    sloc = IntegerField(min_value=-1)
'''

class Udfile(MongoModel):
    TIPO_RAIZ = 'RAIZ'
    TIPO_DIR = 'DIR'
    TIPO_SRC = 'SRC'
    TIPO_FILE = 'FILE'
    TIPO_GIT = 'GIT'
    TIPO_XML = 'XML'
    TIPO_LIBPCAP = 'CAP'
    TIPO = ((TIPO_DIR, 'Subdirectorio'),
            (TIPO_SRC, 'Codigo Fuente'),
            (TIPO_FILE, 'Fichero'),
            (TIPO_GIT, 'Repo git'),
            (TIPO_RAIZ, 'Raiz repo'),
            (TIPO_LIBPCAP, 'Tipo captura'))
    correccion = ReferenceField(Correccion, on_delete=Rf.CASCADE)
    pathrel = CharField(required=True)
    nombre = CharField()
    tipo = CharField(choices=TIPO)  # , required=True)
    hijos = ListField(ReferenceField('Udfile'), blank=True)
    lenguaje = CharField(blank=True)
    sloc = IntegerField(blank=True)
    
    def __str__(self):
        return 'Udfile {} {} {}'.format(self.pathrel, self.nombre, self.tipo)
    
    def clean(self):
        """
        Validamos pbase como ruta absoluta y las demas como relativas a esta.
        :return: True si no han surgido excepciones
        """
        # M_REGEX_PATH PARECE QUE SOLO COGE ABS O . O .., no dir/etc
        # if not re.match(M_REGEX_PATH, self.pathrel):
        #    raise ValidationError(__class__.__name__ + '.pathrel no valida '
        #                          + self.pathrel)
        return True
    
    class Meta:
        indexes = [
            # Indice para simular unique compuesto
            IndexModel([('pathrel', ASCENDING), ('correccion', ASCENDING)],
                       unique=True, name='udfile_pathrel_corr_pk')
        ]


class Udfuente(MongoModel):
    TIPO_PAQUETE = 1
    TIPO_MODULO = 2
    TIPO_FUNC = 3
    TIPO_CLASE = 4
    TIPO_METODO = 5
    TIPO_ATTR = 6
    TIPO_PARAM = 7
    _TIPO = ((TIPO_PAQUETE, TIPO_PAQUETE),
            (TIPO_MODULO, TIPO_MODULO),
            (TIPO_FUNC, TIPO_FUNC),
            (TIPO_CLASE, TIPO_CLASE),
            (TIPO_METODO, TIPO_METODO),
            (TIPO_ATTR, TIPO_ATTR),
            (TIPO_PARAM, TIPO_PARAM))
    udfile = ReferenceField(Udfile, required=True)
    parent = ReferenceField('Udfuente', blank=True)
    nombre = CharField()
    tipo = IntegerField(choices=_TIPO)
    ubicacion = EmbeddedDocumentField('Udfuentecoor')
    snipped = CharField(blank=True)
    
    def __str__(self):
        return '{}: {} {}'.format(__class__.__name__, self.nombre, self.ubicacion)
    
    class Meta:
        indexes = [
            IndexModel([('nombre', TEXT)], name='fuentenombre')
        ]


class Udfuentecoor(EmbeddedMongoModel):
    filaini = IntegerField(blank=False)
    filafin = IntegerField(blank=True)
    col = IntegerField(blank=False, default=-1)
    pos = IntegerField(blank=True)
    
    def __str__(self):
        return '{}: {}:{}'.format(__class__.__name__, self.filaini, self.col)


class GitUser(MongoModel):
    name = CharField()
    email = CharField()
    
    def clean(self):
        import validators
        try:
            return validators.email(self.email)
        except validators.ValidationFailure:
            raise ValidationError(__class__.__name__ + '.email no valido')
    
    class Meta:
        indexes = [
            # Indice que equivale a un unique compuesto por name-email
            IndexModel([('name', ASCENDING), ('email', ASCENDING)],
                       unique=True, name='gituser_name_email_pk')
        ]


class GitBranch(MongoModel):
    correccion = ReferenceField(Correccion)
    nombre = CharField()
    nombre_remote = CharField(blank=True)
    targetid = CharField(min_length=40, max_length=40, blank=True)
    
    def clean(self):
        if self.targetid is not None and \
                not re.match('[a-f0-9]{40}', self.targetid):
            raise ValidationError(__class__.__name__ + '.targetid no valido')
    
    def __str__(self):
        return super().__str__() + ' {} {} {}'.format(
            self.nombre, self.nombre_remote, self.targetid)
    
    class Meta:
        indexes = [
            # Indice para simular unique compuesto por name-email
            IndexModel([('correccion', ASCENDING), ('nombre', ASCENDING)],
                       unique=True, name='gitbranch_corrf_nom_pk')
        ]


class GitCommit(MongoModel):
    """
    Commit
    """
    correccion = ReferenceField(Correccion)
    idhex = CharField(min_length=40, max_length=40)  # , primary_key=True)
    orden = IntegerField()
    author = ReferenceField(GitUser, blank=True)
    committer = ReferenceField(GitUser)
    time = IntegerField()
    offset = IntegerField(min_value=-720, max_value=720)
    mensaje = CharField()
    palabrasclave = ListField(CharField(), blank=True)
    commits_ant = ListField(ReferenceField('GitCommit'), blank=True)
    ficheros = ListField(CharField(), blank=True)
    
    def clean(self):
        if self.idhex is not None and \
                not re.match('[a-f0-9]{40}', self.idhex):
            raise ValidationError(__class__.__name__ + '.idhex no valido')
    
    class Meta:
        indexes = [
            # Indice para simular unique compuesto por name-email
            IndexModel([('correccion', ASCENDING), ('idhex', ASCENDING)],
                       unique=True, name='gitcommit_corrf_idhex_pk')
        ]


class GitAnaly(EmbeddedMongoModel):
    # commitentrega = ReferenceField(GitCommit)
    # commitinicial = ReferenceField(GitCommit, blank=True)  # Para num commits
    numcommits = IntegerField()
    palabras = OrderedDictField()  # Etiqueta y frecuencia en los commits
    intervalos = ListField(IntegerField())  # Interva
    gitusers = ListField(ReferenceField(GitUser))
    gitbranches = ListField(ReferenceField(GitBranch))
    
    class Meta:
        indexes = [
            IndexModel([('actividad', ASCENDING), ('desarrollador', ASCENDING)],
                       unique=True, name='cor_actfec_pk')
        ]


class PruebaMisture(MongoModel):
    """
    Define para la actividad que prueba se va a realizar sobre los repos
    """
    actividad = ReferenceField(Actividad)  # Esto define que prueba hacer.
    titulo = CharField()
    descripcion = CharField()
    comando = CharField()
    salida = ListField(CharField())  # Salida linea o multilinea


class PruebaResultadoMisture(MongoModel):
    """
    Resultado de una PruebaMisture sobre un repositorio concreto (Correccion)
    """
    correccion = ReferenceField(Correccion)
    prueba = ReferenceField(PruebaMisture)
    status = IntegerField()
    exito = BooleanField(blank=True)
    salida = CharField()
    # tipo_salida =
    # path_salida =


class CodeError(MongoModel):
    correccion = ReferenceField(Correccion)
    fichero = CharField()  # ruta relativa en el repositorio
    fila = IntegerField(blank=True)
    columna = IntegerField(blank=True)
    tipo = CharField() # choice E W F C etc o su palabra larga
    codigo = CharField(min_length=4, max_length=4)
    descripcion = CharField(max_length=200)
    # FragmentoCodigoFuenteError


class CuestionExamen(MongoModel):
    ESTADO_FORMULADA = 1
    ESTADO_GUARDADA = 2
    ESTADO_CONFIRMADA = 3
    ESTADO_REVISADA_AUTO = 4
    ESTADO_REVISADA_PROF = 5
    _ESTADO = (
        (1, ESTADO_FORMULADA),
        (2, ESTADO_GUARDADA),
        (3, ESTADO_CONFIRMADA),
        (4, ESTADO_REVISADA_AUTO),
        (5, ESTADO_REVISADA_PROF)
    )
    TIPO_TEXTO = 1
    TIPO_OPCIONES = 2
    TIPO_ABIERTA = 3
    _TIPO = (
        (1, TIPO_TEXTO),
        (2, TIPO_OPCIONES),
        (3, TIPO_ABIERTA)
    )
    correccion = ReferenceField(Correccion)
    tipo = IntegerField(choices=_TIPO)  # choices ??
    contenido = CharField(blank=True)
    pregunta = CharField()  # Obligatoria
    # tipo_respuesta = CharField()  # choices ??
    opciones_respuesta = ListField(CharField(),
                                   blank=True)  # contenidos de las opciones
    opciones_validas = ListField(CharField(), blank=True)
    # una clase opc resp
    respondida = BooleanField(default=False)
    respuesta = CharField()
    fecha_respuesta = DateTimeField(blank=True)
    estado = IntegerField(choices=_ESTADO, default=1)
    
    def clean(self):
        if self.estado not in tuple(x[0] for x in self._ESTADO):
            raise ValidationError(__class__.__name__ + '.estado no valido')
        if self.estado not in tuple(x[0] for x in self._TIPO):
            raise ValidationError(__class__.__name__ + '.tipo no valido')
        if self.tipo == self.TIPO_OPCIONES and \
                (len(self.opciones_respuesta) <= 0 or
                         len(self.opciones_validas) <= 0):
            raise ValidationError(__class__.__name__ +
                                  '.opciones_**** deben contener un listado '
                                  'de valores para {}'.format(self.pregunta))
        elif self.tipo == self.TIPO_TEXTO:
            pass
        elif self.tipo == self.TIPO_ABIERTA:
            pass
            
            # TODO podemos ver si el contenido es mejor la ruta relativa a un
            #  fichero
            # de texto de la ruta del profesor asociada a la corrección de la pregunta

print('IMPORTADO MODELO DE DATOS')

if __name__ == "__main__":
    pass
