import datetime
from datetime import date, datetime

import django_filters
from django.db.models import Q
from django.shortcuts import render
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_rw_serializers import generics
from rest_framework import filters, permissions, serializers, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Agenda, Consulta, Especialidade, Horario, Medico
from .serializers import (
    AgendaSerializer,
    CriarConsultaSerializer,
    EspecialidadeSerializer,
    ListarConsultaSerializer,
    MedicoSerializer,
)

# View e filtros -> Agenda

class AgendaFilter(django_filters.FilterSet):
    medico = django_filters.NumberFilter(field_name='medico__id')
    especialidade = django_filters.NumberFilter(field_name='medico__especialidade__id')
    data_inicio = django_filters.DateFilter(field_name='dia', lookup_expr='gte')
    data_final = django_filters.DateFilter(field_name='dia', lookup_expr='lte')

    class Meta:
        model = Agenda
        fields = ['dia']


class AgendaViewSet(ModelViewSet):
    serializer_class = AgendaSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = AgendaFilter
    permission_classes = (permissions.IsAuthenticated,)
    ordering = ['dia']

    def get_queryset(self):
        queryset = Agenda.objects.filter(dia__gte=datetime.today().date())
        invalidas = []
        for agenda in queryset:
            valido = True
            if agenda.dia == datetime.today().date():
                checagem = []
                for horarios in agenda.horario.all():
                    if horarios.horario < datetime.now().time():
                        checagem.append(horarios.horario)
                if len(checagem) == len(agenda.horario.all()):
                    valido = False
            if not valido:
                invalidas.append(agenda.pk)
        if len(invalidas) > 0:
            for agenda in invalidas:
                queryset = queryset.exclude(pk=agenda)
        return queryset


# View e filtros -> Consulta

def no_past(value):
    today = date.today()
    if value < today:
        raise serializers.ValidationError("A agenda deve conter uma data que não está no passado")


class ConsultaViewSet(generics.ListCreateAPIView):
    today = date.today()
    write_serializer_class = CriarConsultaSerializer
    read_serializer_class = ListarConsultaSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('medico__id', 'especialidade__id', 'dia')
    lookup_field = 'medico__id'
    permission_classes = (permissions.IsAuthenticated,)
    ordering = ['agenda__dia', 'horario']

    def get_queryset(self):
        user = self.request.user
        return Consulta.objects.filter(usuario=user).filter(
            Q(agenda__dia__gt=datetime.today()) |
            Q(agenda__dia=datetime.today()) & Q(horario__gte=datetime.today().time()))


class DeletarConsultaViewSet(generics.RetrieveDestroyAPIView):
    serializer_class = ListarConsultaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        consulta = self.get_object()

        # Retorna horario para a agenda, pois a consulta esta sendo desmarcada
        agenda = consulta.agenda

        horario = Horario.objects.filter(horario=consulta.horario).get()

        # Caso não exista o horario, cria
        if not horario:
            horario = Horario(horario=consulta.horario)
            horario.save()

        agenda.horario.add(horario.id)

        consulta.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Consulta.objects.filter(usuario=self.request.user).filter(
            Q(agenda__dia__gt=datetime.today()) |
            Q(agenda__dia=datetime.today()) & Q(horario__gte=datetime.today().time())
        )


# View e filtros -> Especialidades

class EspecialidadeViewSet(ModelViewSet):
    serializer_class = EspecialidadeSerializer
    queryset = Especialidade.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ('nome')
    lookup_field = 'nome'
    permission_classes = (permissions.IsAuthenticated, )


# View e filtros -> Medicos


class MedicoFilter(django_filters.FilterSet):
    especialidade = django_filters.NumberFilter(field_name='especialidade__id')

    class Meta:
        model = Medico
        fields = ['nome']


class MedicoViewSet(ModelViewSet):
    serializer_class = MedicoSerializer
    queryset = Medico.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = MedicoFilter
    search_fields = ('nome',)
    permission_classes = (permissions.IsAuthenticated,)
