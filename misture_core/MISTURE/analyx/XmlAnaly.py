#! /usr/bin/python3
# encoding: utf-8


import bs4
import os
import os.path as op
import subprocess

"""

1:
Parser sax para cada tipo de lenguaje y actividad concreta (a menos que se haga
un parser bastante exhaustivo para un lenguaje concreto)
+
script para cada lenguaje-actividad que obtenga de aquello ya parseado los
datos de interes (presencia de ciertas etiquetas o atributos, cantidad, secuencia).

2:
    Beautiful soup comprobar que puede obtener el "arbol" de cualquiera de los
    lenguajes xml consideardos (xml, smil), y solo es necesario hacer
    un script para cada actividad para obtener los datos de interes, pero
    sin necesidad de un codigo tan personalizado a la actividad
    (pudiendose incluso parametrizar cierto tipo de comprobaciones en los xml
"""


class AnalyzerXML:

    def get_resumen(self):
        raise NotImplementedError("Debe implementarse este metodo")
    
    
class PDMLAnalyzer(AnalyzerXML):
    
    def __init__(self, origen, destino, traza):
        #print(origen, destino, traza)
        fpdml = op.join(op.normpath(origen), op.normpath(traza+'.pdml'))
        ftraza = op.join(op.normpath(origen), op.normpath(traza))
        if not op.exists(ftraza):
            raise Exception('PDMLAnalizar no existe traza ' + ftraza)

        (status, out) = subprocess.getstatusoutput('tshark -T pdml -r {} > ' \
                '{}'.format(ftraza, fpdml))
        
        if status != 0:
            raise Exception('PDMLAnalizar error generar pdml ', ftraza, fpdml)
        
        if not op.exists(fpdml):
            raise Exception('PDMLAnalizar no existe pmdl' + ftraza)
        self.ruta_traza = ftraza
        self.ruta_pdml = fpdml
    
    def get_resumen(self):
        with open(self.ruta_pdml) as fp:
            soup = bs4.BeautifulSoup(fp, "lxml")
        # fp.__exit__()
        #    raise Exception('No se ha generado pdml de ' + ruta + traza)

        dtrazas = {}
        paquetes = soup.find_all('packet')
        cuenta = len(paquetes)
        for i, packet in enumerate(paquetes):
            # print(type(packet), type(packet))
            for proto in packet.find_all('proto'):
                tipo = proto['name']
                # print(i, type(proto), type(proto['name']), proto['name'])
                if tipo in dtrazas:
                    dtrazas[tipo] += 1
                else:
                    dtrazas[tipo] = 1
        output = 'LA TRAZA llamada.pdml TIENE LA SIGUIENTE COMPOSICION\n' + \
                 'Paquetes {}'.format(cuenta)
        for k, v in dtrazas.items():
            if k not in ('geninfo', 'frame'):
                output += '\n\t{}\t{}'.format(k, v)
        return output
    
    
if __name__ == "__main__":
    pass
    '''
    ruta = '/home/chilli-mint/tmp/misture/4143544956494441445f4341/github/opedraza/'
    traza = 'invite.libpcap'
    gen = PDMLAnalyzer(ruta, ruta, traza)
    print(gen.get_resumen())
    '''

