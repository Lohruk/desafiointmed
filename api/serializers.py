import datetime

from django.db import models
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Agenda, Consulta, Especialidade, Horario, Medico

# Especialidades: 

class EspecialidadeSerializer(ModelSerializer):
    class Meta:
        model = Especialidade
        fields = ('id', 'nome')


# Medicos: 
class MedicoSerializer(ModelSerializer):
    especialidade = EspecialidadeSerializer()

    class Meta:
        model = Medico
        fields = ('id', 'crm', 'nome', 'especialidade')


# Horarios:

class HorarioSerializer(ModelSerializer):
    class Meta:
        model = Horario
        fields = ('horario',)


# Agendas:

class AgendaSerializer(ModelSerializer):
    medico = MedicoSerializer()
    horario = serializers.SerializerMethodField()

    class Meta:
        model = Agenda
        fields = ('id', 'medico', 'dia', 'horario')

    def get_horario(self, instance):
        if instance.dia == datetime.datetime.today().date():
            return [horario.horario.strftime('%H:%M') for horario in instance.horario.filter(horario__gt=datetime.datetime.now().time()).order_by('horario')]
        return [horario.horario.strftime('%H:%M') for horario in instance.horario.all().order_by('horario')]


# Consultas:

class CriarConsultaSerializer(serializers.Serializer):
    agenda_id = serializers.IntegerField()
    horario = serializers.TimeField()

    def validate(self, data):
        from datetime import date
        agenda = Agenda.objects.filter(pk=data['agenda_id']).get()
        # Checagem se a data da consulta não passou
        if agenda.dia < date.today():
            raise serializers.ValidationError("Data de consulta invalida!")
        # Checagem se o horário já passou
        if agenda.dia == date.today():
            if data['horario'] < datetime.datetime.now().time():
                raise serializers.ValidationError("O horário está no passado.")
        # Checagem se o horário está disponível na agenda
        if not Agenda.objects.filter(pk=data['agenda_id'], horario__horario=data['horario']):
            raise serializers.ValidationError("O horario não existe na agenda")
        usuario = self.context["request"].user
        dia = Agenda.objects.filter(pk=data['agenda_id']).get().dia
        for consulta in Consulta.objects.filter(usuario=usuario):
            if dia == consulta.agenda.dia:
                if data['horario'] == consulta.horario:
                    raise serializers.ValidationError("O usuário já possui uma consulta marcada no horário desejado.")
        return data

    def create(self, validated_data):
        usuario = self.context["request"].user

        agenda = Agenda.objects.filter(pk=validated_data['agenda_id']).get()
        horario = None
        for data in agenda.horario.all():
            if data.horario == validated_data['horario']:
                horario = data
                break
        if horario:
            agenda.horario.remove(horario)
        return Consulta.objects.create(agenda=agenda, horario=validated_data['horario'], usuario=usuario)


class ListarConsultaSerializer(ModelSerializer):
    medico = serializers.SerializerMethodField()
    dia = serializers.SerializerMethodField()

    class Meta:
        model = Consulta
        fields = ('id', 'dia', 'horario', 'data_agendamento', 'medico')

    def get_medico(self, instance):
        return MedicoSerializer(instance.agenda.medico).data

    def get_dia(self, instance):
        return instance.agenda.dia
