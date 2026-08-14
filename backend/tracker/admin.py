from django.contrib import admin
from .models import (
    Site, Employe, Coupure, GroupeSession,
    PleinCarburant, ConsommationElectricite, Alerte
)

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_site')
    search_fields = ('nom',)

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'site', 'score_fiabilite', 'date_creation')
    list_filter = ('site', 'date_creation')
    search_fields = ('nom',)

@admin.register(Coupure)
class CoupureAdmin(admin.ModelAdmin):
    list_display = ('site', 'debut', 'fin', 'duree', 'declare_par')
    list_filter = ('site',)
    date_hierarchy = 'debut'

@admin.register(GroupeSession)
class GroupeSessionAdmin(admin.ModelAdmin):
    list_display = ('site', 'employe', 'demarrage', 'arret', 'duree_heures')
    list_filter = ('site',)
    date_hierarchy = 'demarrage'

@admin.register(PleinCarburant)
class PleinCarburantAdmin(admin.ModelAdmin):
    list_display = ('site', 'employe', 'litres', 'prix', 'date')
    list_filter = ('site',)
    date_hierarchy = 'date'

@admin.register(ConsommationElectricite)
class ConsommationElectriciteAdmin(admin.ModelAdmin):
    list_display = ('site', 'mois', 'kwh', 'montant_facture')
    list_filter = ('site',)
    date_hierarchy = 'mois'

@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ('site', 'type_alerte', 'message', 'date', 'resolue')
    list_filter = ('site', 'type_alerte', 'resolue')
    search_fields = ('message',)
    list_editable = ('resolue',)
