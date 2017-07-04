# coding=utf-8
from django.conf.urls import url

from . import views

app_name = 'examen'

urlpatterns = [
    # ex: /polls/
    #url(r'^prueba/*$', views.prueba, name='prueba'),
    url(r'^index/$', views.index, name='index'),
    url(r'^$', views.examenes, name='examenes'),
    url(r'^(?P<idcorreccion>[0-9a-f]+)/$', views.examen, name='examen_id'),
    url(r'^(?P<idcorreccion>[0-9a-f]+)/confirmar/+$',
        views.examen, name='confirmar'),
    url(r'^(?P<idcorreccion>[0-9a-f]+)/pregunta/$', views.pregunta,
        name='pregunta'),
    url(r'^(?P<idcorreccion>[0-9a-f]+)/pregunta/(?P<idpregunta>[0-9a-f]+)/$',
        views.pregunta_id, name='pregunta_id'),
    # url(r'^index/$', views.IndexView.as_view(), name='index_class'),
    url(r'.*', views.redirect_to_index)  # /views.noencontrado*/)
]



