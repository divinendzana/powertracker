from django.contrib import admin
from django.db import models
from .models import (
    Site,
    Employe,
    Coupure,
    SessionGroupe,
    PleineCarburant,
    ConsommationElectrique,
    CalculRatioCarburant,
    SeuillAlerte,
    Alerte,
    ScoreFiabiliteEmploye,
    AuditTrail,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'type_carburant', 'type_groupe', 'puissance_kva', 'actif')
    search_fields = ('nom', 'adresse')
    list_filter = ('type_carburant', 'actif')


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email', 'role', 'site', 'actif')
    search_fields = ('prenom', 'nom', 'email')
    list_filter = ('role', 'actif', 'site')


@admin.register(Coupure)
class CoupureAdmin(admin.ModelAdmin):
    list_display = ('site', 'date_debut', 'date_fin', 'duree_heures', 'statut')
    list_filter = ('statut', 'site')
    search_fields = ('site__nom',)


@admin.register(SessionGroupe)
class SessionGroupeAdmin(admin.ModelAdmin):
    list_display = ('site', 'timestamp_debut', 'timestamp_fin', 'duree_heures', 'statut')
    list_filter = ('statut', 'site')
    search_fields = ('site__nom',)


@admin.register(PleineCarburant)
class PleineCarburantAdmin(admin.ModelAdmin):
    list_display = ('site', 'quantite_litres', 'prix_unitaire_fcfa', 'montant_total_fcfa', 'date_plein')
    list_filter = ('site',)
    search_fields = ('site__nom',)


@admin.register(ConsommationElectrique)
class ConsommationElectriqueAdmin(admin.ModelAdmin):
    list_display = ('site', 'mois_annee', 'consommation_kwh', 'montant_facture_fcfa')
    list_filter = ('site', 'mois_annee')


@admin.register(CalculRatioCarburant)
class CalculRatioCarburantAdmin(admin.ModelAdmin):
    list_display = ('site', 'mois_annee', 'ratio_litres_par_heure', 'donnees_suffisantes')
    list_filter = ('site', 'donnees_suffisantes')


@admin.register(SeuillAlerte)
class SeuillAlerteAdmin(admin.ModelAdmin):
    list_display = (
        'seuil_carburant_pct',
        'seuil_electricite_pct',
        'fenetre_historique_carburant_mois',
        'fenetre_historique_electricite_mois',
    )


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = (
        'site',
        'type_alerte',
        'severite',
        'statut',
        'timestamp_creation',
        'telegram_notification_sent',
    )
    list_filter = ('type_alerte', 'severite', 'statut', 'site')


@admin.register(ScoreFiabiliteEmploye)
class ScoreFiabiliteEmployeAdmin(admin.ModelAdmin):
    list_display = ('employe', 'mois_annee', 'score_final', 'nombre_operations_mois')
    list_filter = ('employe', 'mois_annee')


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'employe', 'action', 'table_cible', 'adresse_ip')
    list_filter = ('table_cible', 'employe')
    search_fields = ('action', 'table_cible')