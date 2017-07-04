#!/usr/bin/env python
# encoding: utf-8


from entities.pymdbodm import PruebaMisture, PruebaResultadoMisture, Actividad

from bson.objectid import ObjectId

from analyx.PruebasAnaly import *



def leer_pruebas(lista, actividad=None):
    pruebas = []
    for pr in lista:
        if len(pr) not in (2, 3):
            raise Exception('leer_pruebas recibe una 3-tupla por prueba')
        # Titulo y comando de la prueba
        if not (isinstance(pr[0], str) and isinstance(pr[1], str)):
            raise Exception('leer_pruebas, titulo y prueba son strings')
        # Tupla de strings admitidos
        if not (isinstance(pr[2], tuple) and
                    all([isinstance(x, str) for x in pr[2]])):
            raise Exception(
                'leer_pruebas el tercer elemento debe ser tupla de str')
        
        prueba = PruebaMisture(titulo=pr[0], comando=pr[1])
        if len(pr) == 3:
            prueba.salida = pr[2]
        pruebas.append(prueba)
        
    #TODO EN INTEGRACIÓN PASAR LA ACTIVIDAD REAL, o refrescar la query buscando su id
    try:   # actividad.pk en lugar de la id
        actividad = Actividad.objects.get({'_id': ObjectId("595930bfd0c409620ec57241")})
    except:
        # TODO MANEJAR ERRORO LOGERROR
        raise
    
    for pr in pruebas:
        prueba.actividad = actividad
        prueba.save()
    return pruebas




def hacer_pruebas(actividad=None):
    #TODO EN INTEGRACIÓN PASAR LA ACTIVIDAD REAL, o refrescar la query buscando su id
    try:
        actividad = Actividad.objects.get({'_id': ObjectId("595930bfd0c409620ec57241")})
        pruebas = PruebaMisture.objects.raw({'actividad': actividad.pk})
        
        # todo falta obtener la ruta de la correccion
        #
        ruta = 'ruta'
        for entrega in actividad.entregas:
            # TODO entrega.correccion y sacar ruta de actividad+corr de la copia del repo para pruebas
            resultados = ejecutar_prueba(ruta, pruebas)
            for res in resultados:
                res.correccion = entrega.correccion
                res.save()
    except:
        # TODO MANEJAR ERROR LOGERROR
        raise



















if __name__ == "__main__":
    PRUEBAS = (('PROBAR PROXY REGISTRAR XML CONF'),
         ('python proxy_registrar.py pr-examen.xml  2>> errores.txt & '),
         (('PROBAR SERVER UA1'),
          ('python uaserver.py ua1-examen.xml  2>> errores.txt & '),),
         (('PROBAR SERVER UA2'),
          ('python uaserver.py ua2-examen.xml  2>> errores.txt & '),),
         (('PROBAR CLIENT UA1'),
          ('python uaclient.py ua1-examen.xml REGISTER 3600  '),),
         (('PROBAR CLIENT UA2'),
          ('python uaclient.py ua2-examen.xml REGISTER 3600  '),),
         (('PROBAR CLIENT UA1'),
          ('python uaclient.py ua1-examen.xml INVITE sip:ua3@iaro.es  '),),)
    
    '''
    SE CAMBIA CON CHDIR Y SE EJECUTARIAN PRUEBAS
    fichpruebapath='pruebafich.txt'
    csv = 'suma,1,2,3,4,5\nresta,31,6,5,4,1\nmultiplica,1,3,5\n' + \
          'divide,300,10,2\ndivide,300,0\n'
    os.system('echo "' + csv + '" > ' + fichpruebapath)
    TEST = (
        ('calc.py suma', 'python2 calc.py 1 suma 2', ('3',)),
        ('calc.py resta', 'python2 calc.py 2.0 resta 1', ('1',)),
        ('calc.py resta operando invalido', 'python2 calc.py dos resta 1',
         ("Error: Non numerical parameters",)),
        ('calcoo.py suma', 'python2 calcoo.py 1 suma 2', ('3',)),
        ('calcoo.py resta', 'python2 calcoo.py 2.0 resta 1', ('1',)),
        ('calcoo.py resta operando invalido', 'python2 calcoo.py dos resta 1',
         ("Error: Non numerical parameters",)),
        (
        'calcoohija.py mult', 'python2 calcoohija.py 2 multiplica 2.5', ('5',)),
        ('calcoohija.py div', 'python2 calcoohija.py 11 divide 4', ('2.75',)),
        ('calcoohija.py div por cero', 'python2 calcoohija.py 1 divide 0.0',
         ('Division by zero is not allowed',)),
        ('calcplus.py', 'python2 calcplus.py ' + fichpruebapath,
         ('15', '15', '15', '15', 'Division by zero is not allowed'))
    '''





