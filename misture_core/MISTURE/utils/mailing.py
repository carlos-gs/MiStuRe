#!/usr/bin/env python3
# encoding: utf-8
"""
Created on 03/10/2014
@author: Carlos González Sesmero
"""

from email import encoders
from email.headerregistry import Address
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from email.utils import format_datetime, localtime, parseaddr, formataddr
from smtplib import SMTP, SMTPException
import os
import re
from traceback import print_exc
from utils.utilidades import Chrono

MAILNAME = 'Carlos'





class mailer:
    """
    Inspirado en http://en.wikibooks.org/wiki/Python_Programming/Email
    MEJORAR:    validación de dirección segun rfc3696??
                gestión de errores y excepciones. Conds carrera por latencia.
                pass no en crudo :O
                ha dejado de funcionar adjuntar ficheros

    Para Gmail, activar https://www.google.com/settings/security/lesssecureapps
    Openmailbox 50 mails/hora. Configs: https://www.openmailbox.org/
    Para envio masivo, usar proveedores smtp (¿libres?):
    https://support.mailpoet.com/knowledgebase/lists-of-hosts-and-their
    -sending-limits/
    office365 (usado urjc) limita 30 por conexion, vamos reconectando hasta
    el limite (
    """
    REINTENTOS = 1  # Número reintentos para .enviar_correo
    smtp_conf = (
        ('smtp.openmailbox.org', 587, 'XXXXXXXX@openmailbox.org',
         'PPPPPP', 50, 50),  # STARTTLS 486 SSL/TLS
        ('smtp.gmail.com', 587, 'XXXXXXXX@gmail.com',
         'PPPPPP', 70, 500),  # 587 tls 465 ssl
        ('outlook.office365.com', 587, 'c.XXXXXXXX@alumnos.urjc.es',
         'PPPPPP', 30, 1000),
        ('smtp.sendgrid.net', 587, 'XXXXXXXX',
         'PPPPPP', 100, 1000, 12000),
    )
    I = 3  # Cual configuración de la tupla elegimos.

    def __init__(self, nombre_rem):
        """
        Establece los parámetros e inicia la conexión.
        :param nombre_rem: Nombre que figurará como remitente de los correos.
        :return:
        """

        self._estadoconexion()
        self.smtp_host = mailer.smtp_conf[mailer.I][0]
        self.smtp_port = mailer.smtp_conf[mailer.I][1]
        self.email_origen = mailer.smtp_conf[mailer.I][2]
        # cambiarlo por la funcion de obtener una pass consola modo texto.
        self.passw= mailer.smtp_conf[mailer.I][3]
        self.nmax_conexion = mailer.smtp_conf[mailer.I][4]
        self.nmax_periodo = mailer.smtp_conf[mailer.I][5]
        self.nombre_origen = nombre_rem
        self._conectar()

    def _conectar(self):
        """
        Rutina de conexión a un servidor SMTP.
        :return:
        """
        try:
            # Conexion con el servidor smtp y procesos para el protocolo.
            server = SMTP(self.smtp_host, self.smtp_port)
            server.ehlo_or_helo_if_needed()  # helo en serv no-ESMTP
            server.starttls()  # Si servidor no lo habilita, yerra.
            server.ehlo_or_helo_if_needed()
            server.login(self.email_origen, self.passw)
            self._estadoconexion(nuevo_serv=server)
        except SMTPException as smtpe:
            raise
        except:
            raise

    def desconectar(self):
        try:
            self.smtpserver.quit()
        except SMTPException:
            raise

    def _estadoconexion(self, nuevo_serv=None, num_enviados=0):
        """
        :param nuevo_serv: Se asigna una conexión smtp ya iniciada para que el
        resto de miembros de la clase mailer hagan uso de ella.
        :param num_enviados: Asigna el atributo de mails enviados en la conexion
        Por defecto se reinicia a 0.
        :return:
        """
        self.smtpserver = nuevo_serv
        self.numenviados = num_enviados

    def enviar_correo(self, correo_dest, asunto, cuerpo, intento=0,
                      *rutas_adjuntos):
        """
        Se envía un correo bajo el nombre indicado a mailer y sobre la conexión
        establecida en este, con los elementos cómunes de un correo, que se
        le pasan como argumentos.
        :param correo_dest:
        :param asunto:
        :param cuerpo:
        :param intento: para indicar el número de reintento.
        :param rutas_adjuntos:
        :return:
        """
        if True in (type(x) is not str for x in (correo_dest, asunto, cuerpo)):
            raise Exception(__name__ + '.sendMail params must be str')

        if self.smtp_host == 'smtp.sendgrid.net':
            origen = 'misture_project@openmailbox.org'
        else:
            origen = self.email_origen
        enviado = False
        # Podríamos verificar cnx sigue, aunque sino ya saltara excepción.
        try:
            # Preparamos las cabeceras de addrs
            fromadrr = Address(self.nombre_origen, addr_spec=origen)
            name, addr = parseaddr(correo_dest)
            toaddr = Address(name, addr_spec=addr)

            # Encapsulamos el mensaje
            msg = MIMEMultipart()  # Para poder combinar fragmentos de <> MIME
            msg['From'] = formataddr((fromadrr.display_name, fromadrr.addr_spec))
            msg['To'] = formataddr((toaddr.display_name, toaddr.addr_spec))
            msg['Subject'] = asunto
            msg['Date'] = format_datetime(localtime())

            # Construir msg (MIME de texto) y añadir al contenedor
            msg.attach(MIMEText(cuerpo, 'plain'))

            #  Adición de los adjuntos, a msg.
            for ruta in rutas_adjuntos:
                rutap = os.path.abspath(ruta)
                if not os.path.exists(rutap):
                    # notificarlo de alguna forma
                    print('{} error:\t fallo adjuntando {} para {}'.format(
                        __name__, rutap, origen))
                    continue
                    
                #with open(rutap) as fp:
                #    part = MIMEText(fp.read(), _subtype='plain')
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(rutap, "rb").read())
                
                encoders.encode_base64(part)
                #  part.add_header('Content-Disposition',
                #   'attachment; filename="{}"'.format(os.path.basename(rutap)))
                part.add_header('Content-Disposition',
                    'attachment; filename="{}"'.format(os.path.basename(rutap)))
                msg.attach(part)
                

            # server.sendmail(fromadrr.addr_spec, tomail, msg.as_string())
            self.smtpserver.send_message(msg)
            enviado = True
            self._incr_numenviados()

        except SMTPException as smtpe:
            print('RECONECTADO y REENVIO POR EXCEPT')
            if intento < mailer.REINTENTOS and not enviado:
                self._conectar()
                self.enviar_correo(correo_dest, asunto, cuerpo, intento+1,
                                   *rutas_adjuntos)
            else:
                raise
        except:
            raise

    def _incr_numenviados(self):
        """
        Metodo que lleva la cuenta de emails enviados y reinicia la conexión
        si hemos superado el maximo teorico por conexion.
        """
        self.numenviados += 1
        if self.numenviados > self.nmax_conexion:
            self._conectar()

    @classmethod
    def _esmailvalido(cls, mail):
        if type(mail) is not str:
            return False
        mail_pat = r'^[_A-Za-z0-9-]+(.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+' + \
                   r'(.[A-Za-z0-9]+)*(.[A-Za-z]{2,})$'
        return re.match(mail_pat, mail)


if __name__ == "__main__":

    def test_sendMail():
        mensajes = ( ('gcarlosonza@gmail.com', 'Gcarlos'),)
        # ('c.gonzalezse@alumnos.urjc.es', 'URJCCarlos'),
        # ('itziar276@gmail.com', 'Itziar PM'),
        # ('c.gonzalez@openmailbox.org', 'openCarlos'),
        # ('charlie7177@hotmail.com', 'hotCarlos'  ),
        # ('itzy_iyeskas@hotmail.com', 'hotItzi'  ),
        # )
        i = 0
        cron = Chrono()
        mensajero = mailer(MAILNAME)
        while i < 10:
            nombre = 'Crono ' + str(i)
            cron.start(nombre)
            try:
                for mail, name in mensajes:
                    #sendgripdeliver.sendpythonapy(...)
                    
                    mensajero.enviar_correo(
                        'gcarlosonza@gmail.com',
                        'Python-correo {} para {}.'.format(i, name),
                        'Aquí tienes el mejor fondo de pantalla:'
                        'http://img1.wikia.nocookie.net/__cb20130510171941/'
                        'horadeaventura/es/images/9/95/'
                        'Hora_de_aventura_de_colores.jpg')
                    """, intento=0)
                        '/home/chilli-mint/Desktop/sqlsintax.pdf',
                        '/home/chilli-mint/Desktop/testo_pfc.txt',
                        '/home/chilli-mint/Desktop/analisis variables.ods',
                        '/home/chilli-mint/Desktop/misture_esquema_general.jpg'
                    )
                        """
                
                i += 1
            except:
                raise
            cron.finish(nombre)
            print('Crono ' + str(i), str(cron.t_count(nombre)))
        print('Total tarda: \n', str(cron.t_count(nombre, cron.TTYPE_splits)))
        mensajero.desconectar()

    test_sendMail()


