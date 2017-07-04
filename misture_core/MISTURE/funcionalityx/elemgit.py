#! /usr/bin/python3
# encoding: utf-8

import collections
from pymodm.common import snake_case
from entities.pymdbodm import *
from analyx import gitAnaly


def analisisgit(pathrepo, correccion):
    # TODO FALTAN ELEVAR LOS ERRORES O IMPRIMIRLOS EN MONGO Y MANEJAR
    # QUE HACER CON LOS OBJETOS YA GUARDADOS EN EL MOMENTO DEL ERROR
    # (P EJ, NO BORRER GITUSERS, si los commits y branch al tener asociada la correccion
    
    # TODO FALTA pasar un contexto o la actividad y correccion para
    # insertar sus identificadores en las impresiones de error en mongo y
    # asociarlo a los commits y branches (para evitar duplicados).
    
    # Acceso al repositorio clonado en local.
    try:
        gu = gitAnaly.GitMisture(pathrepo)
    except:
        # TODO IMPL propagar error para que se guarde en tabla mongo de
        # errores para esa actividad-correccion
        msg = 'analisisgit error accediendo al repositorio ' + pathrepo
        accion = 'Se aborta analisis git en ' + pathrepo
        LogError(msg, accion).save()
        raise
    
    # ACUMULADOS PARA ESTADISTICAS AGRUPADAS Y RELACIONAR REFERENCES DEL ODM
    ramas_saved = []
    com_saved = {}
    users_saved = []
    cum_values = {'times': [], 'palabras_clave': []}
    
    # Obtener ramas.
    ramas = gu.analizarramas()
    for rama in ramas:
        if all([k in rama for k in ('branch', 'remote', 'targetid')]):
            try:
                mdb_rama = GitBranch(correccion=correccion,
                    nombre=rama['branch'],
                    nombre_remote=rama['remote'],
                    targetid=rama['targetid']).save()
                ramas_saved.append(mdb_rama)
            except Exception as exc:
                raise
        else:
            # TODO PROPAGAR O GUARDAR ERROR EN MONGO PARA ESTA ACTIV-CORRECCION
            raise
    
    # A MONGO LOS COMMITS Y LOS USERS GIT ENCONTRADOS
    commits = gu.analizarcommits()
    for commit in reversed(commits):
        if not all(
                [k in commit for k in ('orden', 'commit', 'palabras_clave')]):
            # TODO PROPAGAR O GUARDAR ERROR EN MONGO PARA ESTA ACTIV-CORRECCION
            raise
        
        com = commit['commit']
        
        # SE RECUPERAN O CREAN los name-email de los autores y committers.
        try:
            autor = GitUser.objects.get({
                'name': com.author.name, 'email': com.author.email})
        except DoesNotExist:
            autor = GitUser(name=com.author.name,
                            email=com.author.email).save()
        try:
            committer = GitUser.objects.get({
                'name': com.committer.name, 'email': com.committer.email})
        except DoesNotExist:
            committer = GitUser(name=com.committer.name,
                                email=com.committer.email).save()
        
        if autor not in users_saved:
            users_saved.append(autor)
        if committer not in users_saved:
            users_saved.append(committer)
        
        # REFERENCIAMOS LOS COMMITS PADRE, PREVIAMENTE INSTANCIADOS
        try:
            padres = [com_saved[str(parid)] for parid in com.parent_ids]
        except:
            # TODO VER QUE HAGO CON TODOS LOS COMMITS SI FALLA ASIGNAR PADRES
            raise Exception('analizargit no localizado padre para commit hijo')
        # GUARDAR COMMIT, CON ALGUN DATO Y PADRES.
        try:
            mdb_commit = GitCommit(correccion=correccion,
                idhex=com.hex, orden=commit['orden'],
                author=autor, committer=committer,
                mensaje=com.message, time=com.commit_time,
                offset=com.commit_time_offset,
                palabrasclave=commit['palabras_clave'],
                commits_ant=padres,
                # Ficheros y dirs del primer nivel??
                ficheros=[tr.name for tr in com.tree]
            ).save()
            com_saved[str(com.hex)] = mdb_commit
        except Exception as exc:
            raise
        
        # Almacenamos para las estadisticas agrupadas.
        cum_values['palabras_clave'].extend(commit['palabras_clave'])
        cum_values['times'].append(com.commit_time - com.commit_time_offset)
    
    # ASOCIAMOS EL ANALISIS AL EMBEBBED GitAnaly asociado a Correccion.
    # CALCULAMOS CIERTOS DATOS DEL GRUPO ENTERO DE COMMITS.
    numcommits = len(commits)
    intervalos = [x for x in map(
        lambda x, y: x - y, cum_values['times'][1:], cum_values['times'][:-1])]

    # for x in cum_values['times']:
    #    print(x, datetime.datetime.fromtimestamp(x))
    
    hist = {}
    for p in cum_values['palabras_clave']:
        #  print(p, cum_values['palabras_clave'])
        if p in hist:
            hist[p] += 1
        else:
            hist[p] = 1
    histord = collections.OrderedDict(
        sorted(hist.items(), key=lambda t: (-t[1], len(t[0]))))
    # Almacenamos la información r
    try:
        mdb_gitanaly = GitAnaly(
            numcommits=numcommits,
            palabras=histord,
            intervalos=intervalos,
            gitusers=users_saved,
            gitbranches=ramas_saved)

        # print('intervalos ', [round(x/(3600), 2) for x in
        # mdb_gitanaly.intervalos ])
        # print(mdb_gitanaly)
        
        # ALMACENAMOS EL RESULTADO EN LA CORRECCION.
        correccion.gitanaly = mdb_gitanaly
        return correccion.save()
        
    
    except:
        LogError('analisisgit error guardando en bd Correccion.gitanaly '
                 'con los resultados git de ' + correccion.desarrollador.login,
                 correccion=correccion, actividad=correccion.actividad).save()
        raise

'''
def cruceramacommitgit():
    """
    gc = list(GitBranch.objects.all().only('targetid').values())

    gb = list(GitCommit.objects.all().only('idhex', 'orden').values())
    for dc in gc:
        for db in gb:
            if dc['targetid'] == db['idhex']:
                print(dc, db)
    """
    # Query con el framework agregate que se asemeja a left join.
    # Se cruzan la combinacion commit-rama (local) cuya cuya rama apunta al commit
    print('QUERY CRUZANDO COMMITS Y BRANCH POR IDHEX Y TARGETID. ',
          snake_case(GitBranch.__name__))
    a = GitCommit.objects.aggregate(
        {'$lookup': {'from': snake_case(GitBranch.__name__), 'as': "T_RAMA",
                     'localField': "idhex", 'foreignField': "targetid"}},
        # {'$unwind': {'path': '$T_RAMA', 'preserveNullAndEmptyArrays': True}},
        {'$match': {'$and': [{"T_RAMA": {'$ne': []}},
                             {'T_RAMA.nombre_remote': {'$eq': None}}]}},
        {'$project':
             {'orden': 1, "T_RAMA": 1, 'idhex': 1, 'commits_ant': 1, 'time': 1}}
        # ,{'$out': 'TablaSalidaAgregate'}
    )
    
    for x in list(a):
        print(x)
'''


if __name__ == "__main__":
    pass
    # os.chdir(ruta_base)
    # gitan = git_utils.GitMisture(ruta_base + 'opedraza')
    #ruta_base = '/home/chilli-mint/tmp/misture/4143544956494441445f4341/github/'
    #analisisgit(ruta_base + 'opedraza')
    # cruceramacommitgit()
    
    # RAIZ DE TODAS MIS PRUEBAS CON PYGIT2
    # GitMistureDev.gitprueba(
    # '/home/chilli-mint/tmp/misture/4143544956494441445f4341/github/opedraza')