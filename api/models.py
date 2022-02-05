from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


def no_past(value):
    today = date.today()
    if value < today:
        raise ValidationError("A agenda deve conter uma data que não está no passado")


class Especialidade(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome


class Medico(models.Model):
    nome = models.CharField(max_length=50)
    crm = models.IntegerField()
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE, blank=True)
    email = models.EmailField(blank=True)
    tel = models.IntegerField(blank=True)

    def __str__(self):
        return self.nome


class Horario(models.Model):
    horario = models.TimeField()

    def __str__(self):
        return f'{self.horario}'


class Agenda(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, unique_for_date="dia")
    dia = models.DateField(validators=[no_past])
    horario = models.ManyToManyField(Horario)

    def __str__(self):
        return f"{self.medico}, {self.dia}"


class Consulta(models.Model):
    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE)
    data_agendamento = models.DateTimeField(auto_now_add=True)
    horario = models.TimeField()
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f"Médico {Agenda.medico}, dia: {Agenda.dia}"
