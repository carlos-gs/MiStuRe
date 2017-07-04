#!/usr/bin/env python3
# encoding: utf-8

from analyx.XmlAnaly import *
from entities.pymdbodm import TrazaXML,Udfile, LogError


class FuncXML:
    SMIL = 'smil'
    PDML = 'pdml'
    
    def __init__(self, tipo, origen='', destino='', nombre=''):
        try:
            if tipo == FuncXML.PDML:
                self.analizador = PDMLAnalyzer(origen, destino, nombre)
            else:
                self.analizador = AnalyzerXML(origen)
        except:
            raise
    
    def resultados(self):
        return self.analizador.get_resumen()


def funcionalidadXML(tipo, ruta, correccion, indicaciones={}):
    # OBTENER LOS FICHEROS DE ESE ALUMNO CONCRETO
    udfiles = Udfile.objects.raw(
        {'$and': [{'tipo': Udfile.TIPO_LIBPCAP},
                  {'correccion': correccion.pk}]})
    nombres = set([x['pathrel'] for x in udfiles.only('pathrel').values()])
    #print('\t', tipo, correccion.pk, udfiles.count(), ruta, nombres)
    for nombre in nombres:
        try:
            gen = FuncXML(tipo, ruta, ruta, nombre)
            trazas = gen.resultados()
            #print(trazas)
            resultado = TrazaXML(correccion=correccion, fichero=nombre,
                                 traza=trazas).save()
            
        except Exception as e:
            e=LogError(descripcion='funcionalidadXML error para ' +
                correccion.desarrollador.login, correccion=correccion).save()
            continue


    


if __name__ == "__main__":
    
    #ruta = '/home/chilli-mint/tmp/misture/4143544956494441445f4341/github' \
    #       '/opedraza/'
    traza = 'invite.libpcap'
    
    #gen = FuncXML(FuncXML.PDML, ruta, ruta, traza)
    #print(gen.resultados())
