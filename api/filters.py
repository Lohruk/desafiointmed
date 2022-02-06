import datetime
from datetime import date, datetime

import django_filters

from .models import Agenda, Medico


class AgendaFilter(django_filters.FilterSet):
    medico = django_filters.NumberFilter(field_name='medico__id')
    especialidade = django_filters.NumberFilter(field_name='medico__especialidade__id')
    data_inicio = django_filters.DateFilter(field_name='dia', lookup_expr='gte')
    data_final = django_filters.DateFilter(field_name='dia', lookup_expr='lte')

    class Meta:
        model = Agenda
        fields = ['dia']



class MedicoFilter(django_filters.FilterSet):
    especialidade = django_filters.NumberFilter(field_name='especialidade__id')

    class Meta:
        model = Medico
        fields = ['nome']

