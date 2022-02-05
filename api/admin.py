from django.contrib import admin

from .models import Agenda, Especialidade, Horario, Medico

admin.site.register(Agenda)
admin.site.register(Horario)
admin.site.register(Medico)
admin.site.register(Especialidade)
