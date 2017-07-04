
import datetime

import bson
from bson.objectid import ObjectId
# Formulario de login de django
# Para poder controlar el auth+login que hace automaticamente django.
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

# Importacion desde misture_core
from entities.pymdbodm import LogError, CuestionExamen, \
    Correccion, \
    UsuarioMisture
from .forms import *  # Importo los forms de la app examen

from random import randint

# import pymodm.queryset


# Create your views here.


'''
def prueba(request):
    print('PASO POR PRUEBA')
    try:
        context = {'misture_error': {'mensaje': 'mensaje prueba error'} }
        return render(request, 'dj_misture_err.html', context)
    except Exception as e:
        context = {'misture_error': {'mensaje': str(e)} }
        return render(request, 'dj_misture_err.html', context)
'''


def index(request):
    context = {}
    return render(request, 'base.html', context)


def redirect_to_index(request):
    return HttpResponseRedirect(reverse('examen:index', args=()))


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def noencontrado(request):
    return HttpResponse("URL NO ESPERADA PARA LA APLICACION EXAMEN")

'''
class IndexView(generic.ListView):
    template_name = 'examen/index.html'
    context_object_name = ''
'''

@login_required()
def examenes(request):
    
    us = request.user.username
    
    # RECUPERAR CORRECCIONES ASOCIADAS AL USUARIO
    try:
        usmisture = UsuarioMisture.objects.get({'_id': us})
        correcciones = Correccion.objects.raw({'desarrollador': usmisture.pk})
        ncorrecciones = correcciones.count()
    except Correccion.DoesNotExist:
        raise
    except (bson.errors.InvalidId, Exception) as e:
        raise e
        # Id invalido, nulo o multiples usuarios misture
        context = {'misture_error': {'mensaje': 'ERROR RECUPERANDO LOS DATOS'} }
        return render(request, 'dj_misture_err.html', context)
    context = {'correcciones': correcciones, }
    return render(request, 'examenes.html', context)

@login_required()
def examen(request, idcorreccion=None):
    # Lista las preguntas del examen para el la correccion concreta del usuario
    # Y si esta contextada.

    us = request.user.username
    
    # RECUPERAR LAS CUESTIONES DE LA CORRECCION PARA EL USUARIO
    try:
        usmisture = UsuarioMisture.objects.get({'_id': us})
        correccion = Correccion.objects.get({'$and': [
            {'desarrollador': usmisture.pk, '_id': ObjectId(idcorreccion)}]})
        cuestiones = CuestionExamen.objects.raw({'correccion': correccion.pk})
        ncuestiones = cuestiones.count()
        sinconfirmar = cuestiones.raw({
            'estado':{'$lt': CuestionExamen.ESTADO_CONFIRMADA}}).count()
        #print(cuestiones.count(), correccion, usmisture, sinconfirmar, idcorreccion)
    except (bson.errors.InvalidId, Exception) as e:
        # raise e
        context = {'misture_error': {'mensaje': 'ERROR RECUPERANDO DATOS'}}
        return render(request, 'dj_misture_err.html', context)
    
    
    if request.method == 'GET':
        # El contexto incluye un formulario para confirmar respuestas.
        context = {'cuestiones': cuestiones, 'idcorreccion': idcorreccion,
            'flag_sin_confirmar': sinconfirmar > 0, 'correccion': correccion,
            'form':{'confirmar': ConfirmarForm({'idcorreccion': idcorreccion})}}
        return render(request, 'examen.html', context)
    
    elif request.method == 'POST':
        form = ConfirmarForm(request.POST)
        if form.is_valid():
            idcorr = form.cleaned_data['idcorreccion']
            try:
                if not idcorr == idcorreccion:
                    raise Exception('FORMULARIO DE CONFIRMAR EXAMEN MANIPULADO')
            
                cuestiones.raw({'estado': {'$lt':
                    CuestionExamen.ESTADO_CONFIRMADA}}).update(
                    {"$set": {"estado": CuestionExamen.ESTADO_CONFIRMADA}})
            except Exception as e:
                # raise e
                context = {
                    'misture_error': {'mensaje': 'Error al confirmar'}}
                return render(request, 'dj_misture_err.html', context)
            return HttpResponseRedirect(reverse('examen:examen_id',
                                                args=(idcorr,)))
        else:
            return HttpResponse('ERROR, OPERACION NO VÁLIDA')
    else:
        return HttpResponse('ERROR, OPERACION NO VÁLIDA')


@login_required()
def pregunta(request, idcorreccion=None):
    '''
    Redirige a otra pregunta sin contextar del usuario para la correccion dada.
    :param request:
    :param idcorreccion:
    :return:
    '''
    us = request.user.username
    try:
        usmisture = UsuarioMisture.objects.get({'_id': us})
        correccion = Correccion.objects.get({'desarrollador': usmisture.pk,
                                             '_id': ObjectId(idcorreccion)})
        preguntas = CuestionExamen.objects.raw({'correccion': correccion.pk,
                                    'estado': CuestionExamen.ESTADO_FORMULADA})
        npendientes = preguntas.count()
        prand = randint(0, max(0, (npendientes-1)))
        pregunta = preguntas.skip(prand).first()
    except CuestionExamen.DoesNotExist as dne:
        # Si no hay mas sin responder, redirección al listado de cuestiones.
        return HttpResponseRedirect(reverse('examen:examen_id',
                                            args=(idcorreccion,)))
    except Exception as e:
        # raise e
        context = {'misture_error': {'mensaje': 'ERROR RECUPERANDO LOS DATOS'} }
        return render(request, 'dj_misture_err.html', context)
    return HttpResponseRedirect(reverse('examen:pregunta_id',
                                        args=(idcorreccion, pregunta.pk,)))


@require_http_methods(["GET", "POST"])
@login_required()
def pregunta_id(request, idcorreccion=None, idpregunta=None):
    
    us = request.user.username
    
    # RECUPERAR PREGUNTA ORIGINAL EN MONGO PARA LOS PARAMETROS DADOS
    try:
        usmisture = UsuarioMisture.objects.get({'_id': us})
        correccion = Correccion.objects.get({'$and': [
            {'desarrollador': usmisture.pk, '_id': ObjectId(idcorreccion)}]})
        cuestion = CuestionExamen.objects.get({'correccion': correccion.pk,
                                    '_id': ObjectId(idpregunta)})
        preguntas = CuestionExamen.objects.raw({'correccion': correccion.pk,
            'estado': CuestionExamen.ESTADO_FORMULADA}).only('pk', 'correccion')
        npendientes = preguntas.count()
    except (bson.errors.InvalidId, Exception) as e:
        # raise e
        context = {'misture_error': {'mensaje': 'ERROR RECUPERANDO LOS DATOS'} }
        return render(request, 'dj_misture_err.html', context)
    
    
    #print('Usuario {}<br>Id correccion {}<br>Id pregunta {}'
    #                    '<br>Te quedan {} preguntas por contextar'.format(
    #                    us, correccion.pk, cuestion.pk, npendientes))
    
    if request.method == 'GET':
        context = {'cuestion': cuestion,
                   'form': {'agregar': CuestionExamenForm()},
                   'preguntas_pendientes': npendientes}
        return render(request, 'pregunta.html', context)
    
    elif request.method == 'POST':
        # VALIDAR CONTENIDOS DEL FORMULARIO Y LA CUESTION EXTRAIDA
        try:
            # Recogida del valor de respuesta
            opc_resp = request.POST['respuesta']
        except Exception as exc:
            # raise exc
            context = {'misture_error': {'mensaje':
                    'Error, parámetros del formulario no encontrados'}}
            return render(request, 'dj_misture_err.html', context)
        
        # Segun el tipo de cuestion, se procesa la respuesta.
        if cuestion.tipo == CuestionExamen.TIPO_OPCIONES:
            try:
                nopc = int(opc_resp)
                nopciones = len(cuestion.opciones_respuesta)
                # if el numero de opcion esta dentro del rango de la lista...
                if nopc > nopciones:
                    raise ValidationError(
                        'Se esperaba la opcion {} sobre {} '.format(
                            opc_resp, nopciones
                        ))
                # Asociamos la respuesta la opcion elegida
                respuesta = cuestion.opciones_respuesta[nopc-1]
            except Exception as exc:
                #raise exc
                context = {'misture_error': {'mensaje':
                        'Error recuperando la respuesta. ' + str(exc)}}
                return render(request, 'dj_misture_err.html', context)
        elif cuestion.tipo == CuestionExamen.TIPO_TEXTO:
            respuesta = opc_resp
        elif cuestion.tipo == CuestionExamen.TIPO_ABIERTA:
            respuesta = opc_resp
        else:
            context = {'misture_error': {'mensaje':
                        'CuestionExamen.tipo no esperada ' + cuestion.tipo}}
            return render(request, 'dj_misture_err.html', context)
        
        # RELLENAR RESPUESTA SOBRE LA PREGUNTA EN MONGO
        if cuestion.estado < CuestionExamen.ESTADO_CONFIRMADA:
            cuestion.respondida = True
            cuestion.respuesta = respuesta
            cuestion.estado = CuestionExamen.ESTADO_GUARDADA
            cuestion.fecha_respuesta = datetime.datetime.now()
            cuestion.save()
        else:
            LogError(descripcion='Django examen intento de editar pregunta {}'
                     'ya confirmada'.format(str(cuestion.pk)),
                     correccion=cuestion.correccion).save()
            context = {'misture_error': {'mensaje': 'No se puede contextar' +
                                         'una pregunta ya confirmada'}}
            return render(request, 'dj_misture_err.html', context)
            
        
        #print('POST a pregunta con los parametros {} {} {}\tque representa {}'.
        #      format(usuario, idcorreccion, idpregunta, respuesta ))
        
        # Redirigimos a la url que maneja que nueva cuestión preguntar.
        return HttpResponseRedirect(reverse('examen:pregunta',
                                            args=(idcorreccion,)))

 

    
    
        



