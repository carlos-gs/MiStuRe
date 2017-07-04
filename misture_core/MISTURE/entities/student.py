#!/usr/bin/env python3
# encoding: utf-8
'''
Created on 03/10/2014
@author: Carlos González Sesmero
'''
import sys
import os
import datetime
import urllib.parse

import utils.utilidades as Mutils


class MistureSettingsError(Exception):
    pass

class StudentError(Exception):
    """ Excepción personalizada para eventos de la clase Student """

    def __init__(self, excMsg):
        sys.stdout.write(excMsg + '\n')


class Student(object):
    """
        Clase que administra, almacena y representa los datos necesarios 
        para ejecutar las correcciones de un alumno y sus resultados.
    """

    def __init__(self, username, resultPath, errorPath, teachPath, gitlogPath,
                 gitPath='',
                 githubUrl=''):
        """
           Inicialización de atributos de paths, urls y preparación
           del repositorio del alumno según su existencia y sea remoto o no.
        """
        self.username = username
        # Assume actual dir if paths are relative.
        self.resultPath = os.path.abspath(resultPath)
        self.errorPath = os.path.abspath(errorPath)
        self.teachPath = os.path.abspath(teachPath)  # May be shared.
        self.gitlogPath = os.path.abspath(gitlogPath)
        # Not-joinly-opcional git-related params
        self.gitPath = os.path.abspath(gitPath) if gitPath is not '' else ''
        self.githubUrl = self._verifyGitUrl(githubUrl)
        '''
        # Validar paths segun su uso previsto y es inadecuado => raise exc
        # También cocinar la url con urlparse para que sea git://.....git
        # CODIGO POR ESCRIBIR
        '''
        # Init file's alumn. No teachPath
        try:
            open(self.resultPath, 'w').close()
            open(self.errorPath, 'w').close()
            # open(self.gitlogPath, 'w').close()
        except:
            raise StudentError(
                '[{}]: error al inicializar ficheros de alumno {}'
                .format(self.username))
        ''' Activar esto cuando usemos repositorios y no solo dir de fich
        try:
            self._preprocessRep()
        except StudentError:
            raise  # re-raise
        except:
            raise StudentError('[{}]: error NO PREVISTO al clonar {}'
                             .format(self.username, self.githubUrl.geturl()))
        '''
    
    def _preprocessRep(self):
        """
           Preparación del repositorio de alumno según los atributos
           self.githubUrl y self.gitPath y el self.username del alumno.
        """
        # Clone remote else assume local else raises exception.
        gitRemoteUrl = self.githubUrl.geturl()
        if not gitRemoteUrl is '':
            if self.gitPath is '':
                self.gitPath = os.path.abspath('tmpRep-{}{}'
                                               .format(self.username, str(
                    hash(datetime.datetime.now()))))
            status = os.system('git clone ' + gitRemoteUrl + ' ' + self.gitPath)
            if status != 0:
                self.writeErrLogs('error al clonar {}'.format(gitRemoteUrl))
                raise StudentError('[{}]: error al clonar {}'
                                   .format(self.username, gitRemoteUrl))
            print('Para {} clonado en {} el repositorio {}'
                  .format(self.username, self.gitPath, gitRemoteUrl))
        elif not self.gitPath is '':
            status = os.system('git --git-dir={}/.git status -s ' +
                               '> /dev/null'.format(self.gitPath))
            if status != 0:
                raise StudentError('[{}]: Error, repo local {} no existe'
                                   .format(self.username, self.gitPath))
            print('No indicado repo remoto para {}, se usa {} como local'
                  .format(self.username, self.gitPath))
        else:
            raise StudentError('[{}]: Error, ni [{}] ni [{}] son repos válidos'
                               .format(self.username, self.gitPath,
                                       self.githubUrl.geturl()))
            # git ls-remote git://github.com/user/repo.git #0 success 128 failure
            #  git --git-dir=dirrepo/.git status -s > /dev/null
    
    def _verifyGitUrl(self, giturl):
        """
            Metodo que verifica una url como potencial remota de git (gitHub)
            @return: urllib.parse.ParseResult
            @raise: StudentError
        """
        gUrl = urllib.parse.urlparse(giturl)
        gPath = gUrl.path.split('/')
        if giturl is '':
            return gUrl
        if (not gUrl.scheme in ['http', 'https', 'git'] or not
            gUrl.netloc == 'github.com' or not len(gPath) == 3 or not
            gPath[0] == '' or '' in gPath[1:]):
            raise StudentError('[{}]: Error, {} no es url de repo valida'
                               .format(self.username, gUrl.geturl()))
        return gUrl
    
    def writeErrLogs(self, errormsg):
        """
            Impresión de errormsg a los ficheros de error
            de alumno y profesor asociados.
        """
        Mutils.addErrorToFiles('[{}]: {}'.format(self.username, errormsg),
                               self.errorPath, self.teachPath,
                               in_strerr=False)

    def writeResultStud(self, msg):
        Mutils.writeFiles(msg, self.resultPath)

    def writeResultTeach(self, msg):
        Mutils.writeFiles(msg, self.teachPath)






class MistureMember:

    def __init__(self):
        self.username
        self.mail
        # paths no fijos, que dependan del estado del config mezclado
        # de algun dato o variable propio del miembro.

    def obtenerPath(self):
        # de config y unas claves más el prpio nombre de miembro
        # yde otros campos como curso o practica deben salir los paths
        # es decir, a lo mejor hay que idear una fun mas global
        # o un obtenerPath(tipopath=temporalesalumno, para
        # curso tal, practica tal y alumno tal.
        pass


class Teacher(MistureMember):

    def __init__(self, conf_obj):
        self.name
        self.errorPath
        self.resultPath

    @staticmethod
    def getinfo(settings_teachers_dict):
        dict = settings_teachers_dict
        if type(dict) != dict:
            raise MistureSettingsError('Error extracting teacher settings')


class Course:
    # falta asociar el curso a alumnos, estos se suscriben en sus pracicas.
    def __init__(self, conf_obj):
        self.name
        self.teachers = []
        self.students = []


class Course_Task:

    def __init__(self, conf_obj, course):
        self.sortname
        self.name
        self.description
        self.course


if __name__ == "__main__":
    a = Student(username='carlos',
                resultPath='/home/chilli/pythonpruebas/res',
                errorPath='/home/chilli/pythonpruebas/err',
                teachPath='/home/chilli/pythonpruebas/tea',
                gitlogPath='/home/chilli/pythonpruebas/glp',
                gitPath='',  # '/home/chilli/pythonpruebas/MiStuRe'
                githubUrl='git://github.com/carlos-gs/MiStuRe')
