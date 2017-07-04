#!/usr/bin/env python
# encoding: utf-8
'''
IMPORTANTE: instalados python3 (>=3.4.0) y python2 (>=2.7)
MainAnaly -- shortdesc

MainAnaly is a description

It defines classes_and_methods

@author:     Carlos Gonzalez Sesmero

@copyright:  2017

@license:

@contact:    gcarlosonza@gmail.com
@deffield    updated: Updated

@requires: pep8 pylint BeautifulSoup4

* For future releases.
'''





import sys
sys.path.append('/home/chilli-mint/Dropbox/MiStuRe/misture_core/MISTURE')

import utils.utilidades as Mutils

from funcionalityx.general import mainActividad
from funcionalityx.elemxml import FuncXML




def main(argv=None):
    # If main aren't call with pars, it get them from argv of console.
    if argv is None:
        argv = sys.argv[1:]
        
        
if __name__ == "__main__":

    
    # COnfiguramos la entrega git/local

    actividad = {
        'profesor': ('grex',
                     'gcarlosonza@gmail.com',
                     '/home/chilli-mint/tmp/misture/p6ptavi/profesor/'),
        'descripcion': 'Práctica 6 de PTAVI',
        'ruta': '/home/chilli-mint/tmp/misture/p6ptavi/ejecucion/'
    }

    # lista_login_github = [("opedraza", "olallasanchez")]
    lista_login_github = [
        ("iarranz", "igarag"),
        ("smarin", "silviamaa"),
        ("miriammz", "miriammz"),
        ("rgalan", "raquelgalan"),
        ("jmarugan", "jfernandezmaru"),
        ("jcdb", "jcdb"),
        ("maferna", "mghfdez"),
        ("mtejedor", "mtejedorg"),
        ("apavo", "apavo"),
        ("oterino", "aoterinoc"),
        ("ndiaz", "nathdiaza"),
        ("crodrigu", "crodriguezgarci"),
        ("ilope", "ilope236"),
        ("opedraza", "olallasanchez"),
        ("calvarez", "calvarezpe"),
        ("dpascual", "dpascualhe"),
        ("avera", "Abel-V"),
        ("amoles", "alvaromv83"),
        ("aramas", "aramas"),
        ("jbaos", "JaviBM11"),
        ("rsierra", "rsierrangulo"),
        ("imalo", "nmalo5"),
        ("mireya", "mireepink"),
        ("albagc", "albagcs"),
        ("rpablos", "raquelpt"),
        ("cgarcia", "celiagarcia"),
        ("lyanezgu", "lyanezgu"),
        ("omarled", "auronff10"),
        ("roger", "rogerurrutia"),
        # "lsoria", "lsoriai"),
        ("zhiyuan", "ziyua"),
        ("mcapitan", "mcapitan"),
        ("juanmis", "Jmita"),
        ("molina", "jmartinezmolina"),
        ("afrutos", "alejandrodefrutos"),
        # "carlosjloh", "CarlosJLoH"),
        ("sagun", "caarrieta")
    ]
    # github_dict = collections.OrderedDict(lista_login_github)

    lista_entrega = [(x[0], 'http://github.com/' + x[1] + '/ptavi-p6/')
                     for x in lista_login_github]





    #####################################################################


    time = Mutils.Chrono()  # Mutils.Chrono()
    time.start('Principal')

    # Generamos la actividad y entregas a partir de la información inicial.
    time.start('INICIAR')
    actividad = mainActividad(lista_entrega, actividad)
    '''
    actividad.iniciar_rutas(borrarbase=True) # Borramos base e inicializamos.
    actividad.iniciar_rutas_login()
    time.finish('INICIAR')
    print('INICIAR', time.t_count('INICIAR'), 'seconds.')
    # DESCARGAMOS LOS REPOSITORIOS
    time.start('COPIADO')
    actividad.descargar_repos()
    actividad.preparar_entorno_pruebas()
    time.finish('COPIADO')
    print('COPIADO', time.t_count('COPIADO'), 'seconds.')
    
    # ANALISIS DE LOS FICHEROS DEL REPOSITORIO
    time.start('FICHEROS')
    actividad.fun_fuentes()
    time.finish('FICHEROS')
    print('FICHEROS', time.t_count('FICHEROS'), 'seconds.')
    
    # ANALISIS DE GIT
    time.start('GIT')
    actividad.fun_git()
    time.finish('GIT')
    print('GIT', time.t_count('GIT'), 'seconds.')

    # ANALISIS DE ELEMENTOS DE CODIGO PYTHON
    time.start('PYTHON')
    actividad.fun_pyelements()
    time.finish('PYTHON')
    print('PYTHON', time.t_count('PYTHON'), 'seconds.')

    # ANALISIS DE CHECKS DE CODIGO PYTHON
    time.start('CHECKS')
    actividad.fun_codecheck(codigos_exc='E125,E127,E128,E999')
    time.finish('CHECKS')
    print('CHECKS', time.t_count('CHECKS'), 'seconds.')
  
    # ANALISIS DE XML-PDML
    time.start('XML')
    actividad.fun_xml(FuncXML.PDML)  # Seleccionado tipo TRAZA PARA PDML
    time.finish('XML')
    print('XML', time.t_count('XML'), 'seconds.')
    '''
    
    # GENERAR EXAMEN
    time.start('EXAMEN')
    actividad.fun_examen()
    time.finish('EXAMEN')
    print('EXAMEN', time.t_count('EXAMEN'), 'seconds.')
    
    # PRUEBAS
    '''time.start('PRUEBAS')
    actividad.fun_pruebas()
    time.finish('PRUEBAS')
    print('PRUEBAS', time.t_count('PRUEBAS'), 'seconds.')
    '''

    # IMPRESIÓN DE RESUMEN DE ALUMNOS Y TIEMPO.
    time.finish('Principal')
    print('Checked  in {} seconds.'.format(time.t_count('Principal')))
    

    

    
    """
    for name in sorted(conf.students):
        # Finishing, mailing.
        '''Mutils.sendMail('c.gonzalez@openmailbox.org',
                        'Resultados para ' + name,
                        '{}\n'
                        .format(Mutils.readFileFull(al.resultPath)))'''
        # Matamos to_do. Gracias, bmuma!
        for python_file in PYFILES:
            ejec = "ps aux | grep " + python_file + " | awk '{print $2}'"
            for ident in subprocess_getoutput(ejec).split():
                pass
                os_system('kill -9 ' + ident + ' > /dev/null 2>&1')
    """

    sys.exit()

