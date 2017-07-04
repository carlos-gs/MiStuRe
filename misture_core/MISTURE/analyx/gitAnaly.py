#!/usr/bin/env python
# encoding: utf-8

import os
import shutil
import re
import functools

from datetime import datetime, timezone, timedelta

from pygit2 import clone_repository
import pygit2
from pygit2 import *
import collections

from settings.patrones import *
import validators

M_GIT_COMMENT_EXC_SPA = (
    'a', 'y', 'de', 'que', 'ni', 'la', 'sin', 'con',
    'from', 'pull', 'merge', 'request', 'para',
    'programa', 'patch', 'actualizar', '', 'del', 'un', 'en', 'el')
M_GIT_COMMENT_VIP_SPA = ('rtp',)
M_GIT_COMMENT_NORM = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'
}
'''
Capitalizacion y tildes y puntuaciones con letras
cortar por blancos guiones guiones bajos, barras.
excluir palabras irrelevantes
histogramizar
adaptar nuestros algoritmos de la histogramizacion
'''

'''class contenedor:
    
    def __init__(self, *args, **kargs):
        self.ar
    
    def set'''

# TODO Manipular las trazas https://docs.python.org/3/library/traceback.html
class MGitException(Exception):
    
    def __init__(self, clase, msg, *args, **kwargs):
        self.msg = msg
        for i, arg in enumerate(args):
            setattr(self, 'attr'+str(i), arg)
        for k,v in kwargs.items():
            setattr(self, k, v)
        # traceback.print_exc(file=sys.stdout)
        # TODO imprimir o insertar en el error la clase y el mensaje junto args
        pass
    

class GitMisture:
    
    def __init__(self, ruta, url=None):
        """
        Acceso a un repositorio git en ruta o clonado a ruta desde url
        :param ruta:
        :param url:
        :raises `MGitException o excepciones de Pygit2
        """
        if not (isinstance(ruta, str) and re.fullmatch(M_REGEX_PATH, ruta)):
            raise MGitException(__class__, 'Path invalida ',  ruta, url)
        if not (not url or (isinstance(url, str) and validators.url.url(ruta))):
            raise MGitException(__class__, 'URL invalida ', ruta, url)
        if not url:
            self.repo = GitMisture.accederrepolocal(ruta)
        else:
            self.repo = GitMisture.traeremotolocal(url, ruta)
        
    @staticmethod
    def traeremotolocal(url, rutadest):
        """
        
        :param url: url del repositorio git remoto a clonar
        :param rutadest: ruta local limpia y vuelca el clonado.
        :return: pygit2.Repository del repo,
        :raises: Excepciones si rutadest ya existe. GitError, ValueError u
        otras si falla el clonado.
        """
        try:
            # basedir = os.path.dirname(os.path.abspath(rutadest))
            # if os.path.exists(basedir):
                # os.chdir(basedir)
            if os.path.exists(rutadest):
                # mejor elevar excepcion y se haga fuera y no aqui
                #shutil.rmtree(rutadest)
                raise Exception('{1} no debe existir para clonar hay el repo.\n'
                                'lanza "rm -r {1}"'.format(rutadest))
            else:
                os.makedirs(rutadest)
        except Exception as excp:
            raise
        try:
            # Lo traemos no bare.
            repo = clone_repository(url, rutadest, bare=False)
            # repo.describe()
        except (pygit2.GitError, ValueError, Exception) as excp:
            raise
        return repo
    
    @staticmethod
    def accederrepolocal(ruta):
        """
        
        :param ruta:
        :return:
        :raises Excepciones en caso de error de acceso al repositorio o ruta.
        """
        return pygit2.Repository(ruta)
    
    @staticmethod
    def tiempostr(marca, desplazamiento):
        if not(isinstance(marca, int) and isinstance(desplazamiento, int)):
            raise MGitException(__class__, 'Parametros deben ser int',
                                marca, desplazamiento)
        tzinfo = timezone(timedelta(minutes=desplazamiento))
        dt = datetime.fromtimestamp(float(marca), tzinfo)
        return dt
    
    @staticmethod
    def __extraersignificantes(mensaje: str):
        """
        Dado un str con un mensaje, lo normaliza y trocea en lista de palabras
        o tags tras filtrarlas por listado de exclusiones
        :param mensaje: str con el mensaje del commit.
        :return:
        """
        # print(mensaje)
        
        men = mensaje.lower()
        for k, v in M_GIT_COMMENT_NORM.items():
            men = men.replace(k, v)
        men = re.sub('\b+|\s+|-|\\|_|>|<|#|/|,|\.$|(\d+)|\|', ' ', men)
        men = re.sub('\.', '_', men)  # code.py -> code_py
        # mens = re.split('\s+', men)
        menslist = list(filter((lambda x: x not in M_GIT_COMMENT_EXC_SPA),
                               re.split('\s+', men)))
        # print(men)
        return menslist
    
    def palabrasclave(self, oid_origen=None, incluir=[], excluir=[]):
        if not oid_origen:
            origen = self.repo.head.target
        palabras = {}
        paseo = self.__recorrer(str(oid_origen))
        for comm in paseo:
            mens = self.__extraersignificantes(comm.message)
            palabras[comm.hex] = mens

        # CONTAR COMMITS. UNIR LAS PALABRAS RELEVANTES EN UNA UNICA LISTA
        pal = functools.reduce((lambda x, y: x + y), palabras.values())
 
        hist = {}
        for p in pal:
            if p in hist:
                hist[p] += 1
            else:
                hist[p] = 1
        hist2 = collections.OrderedDict(
            sorted(hist.items(), key=lambda t: (-t[1], len(t[0]))))
        return hist2
        
    @staticmethod
    def commitlog(commit):
        """
        Dado un pygit2.Commit, se imprime parecido a 'git log'
        :param commit:
        :return:
        """
        dt = GitMisture.tiempostr(commit.author.time, commit.author.offset)
        timestr = dt.strftime('%c %z')
        msg = '\n'.join(['commit {}'.format(commit.tree_id.hex),
            'Author: {} <{}>'.format(commit.author.name, commit.author.email),
            'Date:   {}'.format(timestr), '', commit.message])
        #print(msg)
        
    def __recorrer(self, idcommit=None):
        if idcommit is not None and not re.match('[a-f0-9]{40}', idcommit):
            raise Exception('__recorrer, idcommit inicial invalido')
        if self.repo.head_is_unborn:
            raise Exception('__recorrer, la rama no tiene commits')
        origen = self.repo.head.target
        paseo = self.repo.walk(origen, GIT_SORT_TOPOLOGICAL | GIT_SORT_TIME)
        return paseo
        
    def frecuencias(self, idcommit=None):

        frecuencias = []
        paseo = self.__recorrer()
        times = []
        for comm in paseo:
            times.append(comm.commit_time-comm.commit_time_offset)
        intervalos = [x for x in map(lambda x, y: x - y, times[1:], times[:-1])]
        return frecuencias
        
    def analizarcommits(self, idcommit=None):
        '''
        Devolvemos una lista con hex, orden, hex, [commits padre]
        :return:
        '''
        commits = []
        if idcommit is not None and not re.match('[a-f0-9]{40}', idcommit):
            raise Exception('Analizar commits, idcommit inicial invalido')
        
        # TODO FALTA VER QUE HACER SI DAN IDCOMMIT DESDE EL QUE PARTIR y/u
        # otro de inicio.Por defecto vamos a asumri el head
        # if idcommit is not None: origen=self.repositorio.****(idcommit) ...
        
        paseo = self.__recorrer()
        
        # Exploración de commits desde el de referencia hacia antecesores.
        for i, comm in enumerate(paseo):
            #print(i, comm.hex,
            #      self.tiempostr(comm.commit_time, comm.commit_time_offset))
            #print('\t', comm.parent_ids)
            #print([e.name for e in comm.tree])
            # TODO dificil relacionar ramas, obtener el tema de los
            # padres que sea facil luego de meter en mongo.
            commits.append({
                'orden': i,
                'commit': comm,
                'palabras_clave': self.__extraersignificantes(comm.message)
            })
            # print('##### ', comm.author.name, comm.author.email)
            # print('##### ', comm.committer.name, comm.committer.email)
        #  print(commits)
        return commits
    
    def analizarramas(self):
        '''
        Se obtiene info muy básica de las ramas del repo clonado.
        :return: Lista de diccionarios con la info deseada de las ramas.
        '''
        # TODO manejar el eventual caso en que Branch.type es un link o
        # sea un oid pero no sea un Commit.
        ramas = []
        loc_ramas = self.repo.listall_branches(GIT_BRANCH_LOCAL)
        
        for ram in loc_ramas:
            rama = self.repo.lookup_branch(ram, GIT_BRANCH_LOCAL)
            ramas.append(
                {'branch': rama.branch_name, 'remote': None,
                 'targetid': rama.target.hex})
        rem_ramas = self.repo.listall_branches(GIT_BRANCH_REMOTE)
        
        for ram in rem_ramas:
            rama = self.repo.lookup_branch(ram, GIT_BRANCH_REMOTE)
            ramas.append(
                {'branch': rama.branch_name, 'remote': rama.remote_name,
                 'targetid': rama.target.hex})

        return ramas


class GitMistureDev(GitMisture):
    '''
    Pruebas de desarrollo de más funcionalidades de la clase GitMisture.
    '''
    
    @staticmethod
    def evaluarcommits(orepository):
        repo = orepository
        # INVESTIGO COMMITS
        paseo = repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL) #  pygit2.GIT_SORT_TIME)
        print('---------------------------------------------------------------')
        print('CANTIDAD COMMITS ', paseo)
    
        i = 0
        for com in paseo:
            i += 1
            print('COMMIT {} HEX {} ', i, com.hex)
            # print(repo.describe(com))
            # comt = com.commiter
        # '''
            aut = com.author
            print('\t\t|--------------------------------------',type(com),'\n',
                  #'COMMIT: \t\t|', com.message, '|\n', com.hex , '\n',
                  #'DATOS AUTOR ', aut.name, aut.email, aut.time, '\n\t\t',
                  #comt.name, comt.email, comt.time, '\n',
                  #'TP COMMIT ', com.commit_time,  com.commit_time_offset,
                  datetime.utcfromtimestamp(
                  com.commit_time).isoformat(),' fecha legible \n\t\t',
                  'ENC TREEID TREE ',com.message_encoding,com.tree_id, com.tree,
                  'PARENTS ', com.parents) #, com.parents_ids)
            for e in com.tree:
                print('\t\t', e.name)
            # IMPRIMIMOS DATOS DEL COMMIT SIMILAR A UN GIT LOG
            #GitMisture.commitlog(com)
            
            # Pruebas entre commits de una rama y ahead_behind
            if i == 1:
                c1 = com
                cant = c1
            sol1 = repo.ahead_behind(com.hex, c1.hex)
            sol2 = repo.ahead_behind(c1.hex, com.hex)
            print('act-ult {} {} -> {}'.format(com.hex, c1.hex, sol1))
            print('act-ult {} {} -> {}'.format(c1.hex, com.hex, sol2))

            '''
            sol = repo.ahead_behind(com.hex, c1.hex)
            print('DIFERENCIA act-1º  {} Y {} -> ahead-behind {}'.format(c1.hex, com.hex, sol))
            sol = repo.ahead_behind(c1.hex, cant.hex)
            print('DIFERENCIA ant-1º  {} Y {} -> ahead-behind {}'.format(c1.hex, cant.hex, sol))
            sol = repo.ahead_behind(com.hex, cant.hex)
            print('DIFERENCIA act-ant {} Y {} -> ahead-behind {}'.format(cant.hex, com.hex, sol))
            '''
            cant = com  # Pasa a ser el anterior

            #print('DESCRIBE, str Commit Repository, a menudo no puede')
            #print(repo.describe(committish=com, describe_strategy=pygit2.GIT_DESCRIBE_ALL))
            print('\t\t----------------------------------|')
        # '''
        # print(type(com.commit_time), type(com.commit_time_offset)) int int
    
    @staticmethod
    def evaluarbranches(orepository):
        repo = orepository
        # INVESTIGO RAMAS
        #pygit2.Branch.
        pygit2.Repository.listall_branches()
        
        rama = repo.lookup_branch('master')
        print('\nEXTRAIGO RAMA MASTER ', rama)
        print('\nPARA ESA RAMA MASTER: ', rama.branch_name, rama.name, rama.shorthand,
              '\n\t', rama.upstream, rama.upstream_name,  # rama.remote_name,
              '\n\ttiene HEAD', rama.is_head())
        loglog = rama.log()
        for entry in loglog:
            print('\tITERACION LOG de head de rama')
            print('\n\t\t', entry.message, entry.oid_new, #entry.commiter,
                  entry.oid_old)

        ramasl = orepository.listall_branches(pygit2.GIT_BRANCH_LOCAL)
        for nom in ramasl:
            ra = orepository.lookup_branch(nom, pygit2.GIT_BRANCH_LOCAL)
            print(nom, ra, type(ra))
            print('RAMA {}\n\t',
                  '{}\n\t'.format(ra.branch_name),
                  '{} {}\n\t'.format(ra.upstream, ra.upstream_name),
                  '{} {} {}\n\t'.format(ra.name, ra.shorthand, ra.type),
                  '{}\n'.format(ra.target))
        ramasr = orepository.listall_branches(pygit2.GIT_BRANCH_REMOTE)
        for nom in ramasr:
            ra = orepository.lookup_branch(nom, pygit2.GIT_BRANCH_REMOTE)
            print(nom, ra, type(ra))
            print('RAMA {}\n\t',
                  '{} {}\n\t'.format(ra.branch_name, ra.remote_name),
                  # '{} {}\n\t'.format(ra.upstream, ra.upstream_name),
                  '{} {} {}\n\t'.format(ra.name, ra.shorthand, ra.type),
                  '{}\n'.format(ra.target))
    
    @staticmethod
    def evaluareferences(orepository: pygit2.Repository) -> None:
        
        repo = orepository
        # Acceso a los references del repositorio
        refs = repo.listall_reference_objects()
        refnames = repo.listall_references()
        
        print('\nREFERENCIAS DETECTADAS: ', refs, '\n', refnames)
        for ref in refs:
            #repo.describe(committish=ref)
            reflog = ref.log()
            print('REFERENCIA. NOMBRES: ', ref.name, ref.shorthand,
                  'REF_LINK/OID_OBJ-> ', ref.target,
                  'TIPO 0-3 (CONST GIT_REF_*): ', ref.type,
                  '\n\tReference.log()-> ', reflog)
            if ref.type == pygit2.GIT_REF_OID:
                reftype = 'REF_OID'
            elif ref.type == pygit2.GIT_REF_SYMBOLIC:
                reflink = ref.resolve()  # Resolve resuelve el link
                reftype = 'REF_SYMBOLIC'
                print(reflink)
            elif ref.type == pygit2.GIT_REF_LISTALL:
                reftype = 'REF_LISTALL'
            elif ref.type == pygit2.GIT_REF_INVALID:
                reftype = 'REF_INVALID'
            else:
                raise Exception('Valor inválido para Reference.type ', ref.type)
            print(reftype)
            #'''
            for entry in reflog:
                print('\tITERACION LOG de ref Extraida')
                print('\t\t\t|', entry.message, '|\n\t\t\t',
                      entry.oid_old, '->', entry.oid_new)   #, entry.commiter)
                print('\t\t\t', entry.committer.name, entry.committer.email,
                      GitMisture.tiempostr(entry.committer.time,
                                           entry.committer.offset))
            #'''
            GitMistureDev.extraerdereferencia(ref.target, repo)
            print('\n')

    @staticmethod
    def extraerdereferencia(oid: pygit2.Oid, repo: pygit2.Repository) -> None:
        pygit2.Repository
        try:
            a = repo[str(oid)]
        except ValueError:
            raise
        print(str(oid), a)
        if issubclass(a.__class__, pygit2.Reference):
            print('target es un reference')
        elif issubclass(a.__class__, pygit2.Object):
            print('target es un ' + str(a.__class__))
        else:
            print('no es subclase')
                
    @staticmethod
    def obtenerstatsdiff(repo, cfin, cini, wk=False):
        t1, t2 = cini, cfin
        print(type(t1), type(t2), t1, t2)
        # cached=True para index sino WorkingDir cuando Cini=None
        # None, None  es   workingdir->index
        di = repo.diff(cini, cfin, cached=wk)  # , t1)
        # di = repo.diff('HEAD', 'HEAD^')
        diffes = 'DIFF DI {} \n' \
                 'DIFF.stats {} \n' \
                 'DIFF.patch {} -> \n' \
            .format(di, di.stats, type(di.patch))
        # pygit2.DiffStats.
        print(diffes)
        #pygit2.DiffDelta.similarity
        est = di.stats
        estad = 'DIFF STATS CONTENIDO\nINSERCCIONES {}\nDELETIONS {}\n' \
                'FICHEROS CAMBIADOS {}'.format(est.insertions, est.deletions,
                                               est.files_changed)
        print(estad, '\n\n')
        print(di.stats.format(pygit2.GIT_DIFF_STATS_FULL, 100))
        # Iterando sobre el objeto Diff, obtenemos los Patch
        for p in di:
            #
            msg = 'PATCH {}  .DELTA {} .HUNKS {} .LINE_STATS {}'.format(
                type(p), type(p.delta), type(p.hunks), type(p.line_stats))
            print(msg)
            for at in p.hunks:
                print('\t', type(at), at)
            print('\t', type(p.line_stats), p.line_stats)
            
            dl = p.delta
            msgdeltadiff = 'DIFFDELTA {} {} {} {} {}'.format(
               dl.old_file, dl.new_file, dl.status, dl.similarity, dl.is_binary)
            print('\t', msgdeltadiff)
            # Evaluo clases DiffFile
            of , nf = dl.old_file, dl.new_file
            msg3 = 'old_file {} {} {} {} {}'.format(of.path, of.id, of.size,
                                                    of.flags, of.mode)
            msg4 = 'new_file {} {} {} {} {}'.format(nf.path, nf.id, nf.size,
                                                    of.flags, nf.mode)
            print(msg3)
            print(msg4)
            
            print('\nHUNKS {} {}\n'.format(p.hunks, len(p.hunks)))
            for h in p.hunks:
                msgh = '.os {}\n.ol {}\n .ns{}\n .nl {}\n .lin {}\nhd {}\n'\
                    .format(h.old_start, h.old_lines, h.new_start, h.new_lines,
                            h.lines, h.header)
                print(msgh)
                #pygit2.GIT_DIFF
                for h in h.lines:
                    msgl = '.ori {}\n.con {}\n.coff {}\n .ol {}\n .nl {}\nnlin {' \
                           '}\n' \
                        .format(h.origin, h.content, h.content_offset,
                                h.old_lineno, h.new_lineno, h.num_lines)
                    print(msgl)
    
    @staticmethod
    def gitprueba(rutarepo):
        
        # RECUPERO LOS REPOS YA GUARDADOS
        repo = pygit2.Repository(rutarepo)  # )ruta_base + alumno)
        sta = repo.status()
        print(repo.path, repo.workdir, repo.is_bare, repo.is_empty,
              '\n\tSu HEAD: ', repo.head, repo.head.name, repo.head_is_detached,
              repo.head_is_unborn)  # ,repo.default_signature)
        # STATUS DEVUELVE LOS TRACKED CON CAMBIOS NO COMMITEADOS Y UN ID STATUS
        # pygit2.GIT_STATUS_* p. ej ignored 16834 pygit2.GIT_STATUS_IGNORED
        print('STATUS de stage-wk (se fuma .gitignore) ', sta)
        print('PATHs novisiblegit.log ignorado (! add): ', repo.path_is_ignored(
            'novisiblegit.log'), 'repo.status_file', repo.status_file('novisiblegit.log')
        )
        print('PATHs nuevo2.py es ignorado(no add): ', repo.path_is_ignored(
            'nuevo2.py'), 'repo.status_file', repo.status_file('nuevo2.py')
        )
        pygit2.GIT_STATUS_CURRENT
        print('TENEMOS ACCESO AL INDEX, Repository.index ', repo.index)
        print('############ FIN ATTR CLASE REPOSITORY ########################')
    
        khead = str(repo.head.target)
        lola = '2fce12b17579632012d2da4d337af41895033af7'  # ULtimo
        k2 =   '7503e01b1d00b9b3bc0b5de415e93e244944dd4e'  # Primero
        kgrex0 = '7503e01b1d00b9b3bc0b5de415e93e244944dd4e'
        kgrex = '97d5226262364aeacf1046ee5d8ef61c45554f4a'
        # print('GREX {}\nk1 {}\nk2 {}\nkhead {}'.format(kgrex, lola, k2,
        # khead))
        # repo[lola], repo[khead]
        
        #GitMistureDev.obtenerstatsdiff(repo, repo[k2], repo[khead])
        # GitMistureDev.obtenerstatsdiff(repo, repo[khead], None, True)
        
        GitMistureDev.evaluareferences(repo)

        #GitMistureDev.evaluarbranches(repo)

        GitMistureDev.evaluarcommits(repo)
    
        # print('NOTAS ', repo.notes())
        # print(repo.status())
        print('###########################################################',
              # i,
              '###########################################################\n\n')
            

if __name__ == "__main__":
    pass
