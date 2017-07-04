#!/usr/bin/env python3
# encoding: utf-8

# Añadimos el path de MISTURE de modo que sean visibles los paquetes
#import sys
#sys.path.append('/home/chilli-mint/Dropbox/MiStuRe/misture_core/MISTURE')

# Borro la base las colecciones e indices con nuestro metodo personalizado
import entities.mongops
#entities.mongops.borrarindicesevitardups()
#entities.mongops.borrardb()


import pymodm
# from pymongo import MongoClient
# MongoClient().drop_database('misture_mbbd')
pymodm.connect('mongodb://localhost:27017/misture_mbbd_pfc3')
from entities.pymdbodm import *

from bson.objectid import ObjectId

import collections

from analyx import FuentesAnaly, CodeAnaly, gitAnaly, PyGrammarAnaly, \
    PruebasAnaly, OutputAnaly, GenerarExamen, XmlAnaly

from funcionalityx import elemcodecheck, elemgit, elempython, elemxml, \
    examen, pruebas

import utils.utilidades as Mutils





class mainActividad:
    
    def __init__(self, lista_entrega, def_activ, lista_ficheros = []):
        '''
        Inicializamos
        :param lista_entrega: tupla de logines y direcciones github de entrega
        :param def_activ: {profesor, descripcion, ruta}
        :param lista_ficheros: opcional, lista de nombre de fichero esperados
        '''
        #self.actividad = Actividad.objects.get(
        #    {'_id': ObjectId("595bd4f1d0c409043de4f945")})
        
        try:
            # Almacenamos
            corrector = Corrector(login=def_activ['profesor'][0], email=def_activ['profesor'][1]).save()
            # El resto de rutas si no se indican por defecto se crean bajo pbase
            rutas_act = DirectoriosActividad(
                pbase=def_activ['ruta'], pprofesor=def_activ['profesor'][2])
            act = Actividad(descripcion=def_activ['descripcion'],
                            directorios=rutas_act,
                            corrector=corrector).save()
            
            # Generamos en bd los objetos entrega y correccion, por cada alumno
            entregas = []
            correcciones = []
            desarrolladores = []
            
            for alumno in lista_entrega:
                # Generamos también al alumno-desarrollador
                dev = Desarrollador(login=alumno[0]).save() # email=alumno[1]
                # Generamos el objeto correccion por cada alumno
                corr = Correccion(actividad=act, desarrollador=dev).save()
                
                ent = Entrega(desarrollador=dev, modo=Entrega.TIPO_GITURL,
                              ubicacion=alumno[1], correccion=corr)
                
                correcciones.append(corr)
                desarrolladores.append(dev)
                entregas.append(ent)
                
            act.entregas = entregas
            act.desarrolladores = desarrolladores
            
            # Actualizamos en BD la actividad y los datos de entregas relacionados
            self.actividad = act.save()
            
        except:
            raise

    def refresh_actividad(self):
        '''
        Se refresca y devuelve de la bd la info de la actividad de id unico.
        :return:
        '''
        try:
            self.actividad = Actividad.objects.get(
                {'_id':ObjectId(self.actividad.pk)})
            return self.actividad
        except DoesNotExist:
            raise
        except ModelDoesNotExist:
            raise
        except MultipleObjectsReturned:
            raise
         
    def iniciar_rutas(self, borrarbase=False):
        if borrarbase:
            self.actividad.directorios.borrardirectoriosbase()
        self.actividad.directorios.creardirectorios()
    
    def iniciar_rutas_login(self):
        alumnos = self.refresh_actividad().desarrolladores
        listado = [dev.login for dev in alumnos]
        self.actividad.directorios.creardirectorios(paralogines=listado)
    
    def descargar_repos(self):
        
        ents = self.actividad.entregas
        for ent in ents:
            origen = ent.ubicacion
            destino1 = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PENTREGA, ent.desarrollador.login)
            destino2 = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PREPOTMP, ent.desarrollador.login)
            destino3 = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PREPOEJEC, ent.desarrollador.login)
            #print('{}\t{}\t{}\n'.format(destino1, destino2, destino3))
            if Entrega.TIPO_GITURL == ent.modo:
                gitAnaly.GitMisture.traeremotolocal(origen, destino1)
                
            elif Entrega.TIPO_LOCAL == ent.modo:
                shutil.copytree(origen, destino1)
            else:
                LogError(descripcion='descargar repos modo equivocado en la '
                         'entrega de ' + ent.desarrollador.login,
                         actividad=self.actividad)
                continue
            shutil.copytree(destino1, destino2)
            shutil.copytree(destino1, destino3)
            
    def preparar_entorno_pruebas(self):
        # Invoca la generacion de examen para todas las entregas
        ents = self.refresh_actividad().entregas
        # COgemos la ruta del profesor que tiene el subdir ficheros_test
        ruta_origen = self.actividad.directorios.rutapara_login(
            DirectoriosActividad.PPROFESOR, 'ficheros_test')
        if not op.isdir(ruta_origen):
            raise Exception('No existe ruta por defecto de ficheros de test')
    
        for ent in ents:
            corr = ent.correccion
            dev = corr.desarrollador
            # Cargamos la copia del repo que tenemos para ejecutar
            rutadst = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PREPOEJEC, dev.login+'/ficheros_test')
            # Ya se ha producido el guardado en examen
            #print(ruta_origen, rutadst)
            try:
                shutil.copytree(ruta_origen, rutadst)
            except:
                raise
    
    def fun_fuentes(self):
        # Invoca el analisis de fuentes para todas las entregas
        ents = self.refresh_actividad().entregas
        for ent in ents:
            corr = ent.correccion
            dev = corr.desarrollador
            rutarepo = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PENTREGA, dev.login)
            udfiles = FuentesAnaly.obtenerestructura(rutarepo)
            # Se guardan rf a la corr los ficheros en el orden inverso al
            # de creación ya que raiz y dirs referencian a los hijos.
            for fl in reversed(udfiles):
                fl.correccion=corr
                try:
                    fl.save()
                except Exception as e:
                    LogError(correccion=corr, descripcion=str(e)).save()
                
    def fun_git(self):
        # Invoca el analisis de git para todas las entregas
        ents = self.refresh_actividad().entregas
        for ent in ents:
            corr = ent.correccion
            dev = corr.desarrollador
            rutarepo = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PENTREGA, dev.login)
            ret = elemgit.analisisgit(rutarepo, corr)
            # Ya se ha producido el guardado en elemgit
            
    def fun_codecheck(self, codigos_exc):
        # Invoca el analisis de checks de codigo para todas las entregas
        ents = self.refresh_actividad().entregas
        for ent in ents:
            corr = ent.correccion
            dev = corr.desarrollador
            # Si hubiera que retocar el repositorio antes del analisis p.ej.
            # para hacer 2to3 una copia en tenemos la ruta llamada PREPOTMP
            rutarepo = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PREPOTMP, dev.login)
            
            #print('fun_fuentes ruta ' + rutarepo)
            
            ret = elemcodecheck.analisis_errores(rutarepo, corr, codigos_exc)
            # Ya se ha producido el guardado en elemcodecheck
            #print(len(ret), type(ret), ret)

    def fun_pyelements(self):
        # Invoca el analisis de elementos python para todas las entregas
        ents = self.refresh_actividad().entregas
        for ent in ents:
            corr = ent.correccion
            dev = corr.desarrollador
            # Si hubiera que retocar el repositorio antes del analisis p.ej.
            # para hacer 2to3 una copia en tenemos la ruta llamada PREPOTMP
            rutarepo = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PREPOTMP, dev.login)
        
            ret = elempython.analisis_python(rutarepo, corr)
            # Ya se ha producido el guardado en elemcodecheck
            # print(len(ret), type(ret), ret)

    def fun_examen(self):
        # Invoca la generacion de examen para todas las entregas
        ents = self.refresh_actividad().entregas
        # Inicio el generador de preguntas, que carga las del json.
        ruta_examen = self.actividad.directorios.rutapara_login(
            DirectoriosActividad.PPROFESOR, 'examen')
        # TODO averiguar como reutilizar un mismo registro para diferentes pk
        #gen = GenerarExamen.Generador(ruta_examen, 'examen.json')
        for ent in ents:
            gen = GenerarExamen.Generador(ruta_examen, 'examen.json')
            corr = ent.correccion
            dev = corr.desarrollador
            # Para cada alumno le generamos distintas preguntas de autoria
            # y se las guardamos.
            ret = examen.generarExamen(gen, corr)
            # Ya se ha producido el guardado en examen
    
    def fun_pruebas(self):
        pass

    def fun_xml(self, TIPO):
        # Invoca la generacion de examen para todas las entregas
        ents = self.refresh_actividad().entregas
        for ent in ents:
            corr = ent.correccion
            dev = corr.desarrollador
            # Para cada alumno le generamos distintas preguntas de autoria
            # y se las guardamos.
            ruta = self.actividad.directorios.rutapara_login(
                DirectoriosActividad.PENTREGA, dev.login)
            ret = elemxml.funcionalidadXML(elemxml.FuncXML.PDML, ruta, corr)
            # Las trazas con las pruebas hechas ya se guardan en bd
    

