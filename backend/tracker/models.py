from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Site(models.Model):
    MAISON = 'maison'
    RESTAURANT = 'restaurant'
    TYPE_CHOICES = [
        (MAISON, 'Maison'),
        (RESTAURANT, 'Restaurant'),
    ]

    nom = models.CharField(max_length=100)
    type_site = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return self.nom


class Employe(models.Model):
    nom = models.CharField(max_length=100)
    code_pin = models.CharField(max_length=10)  # à hasher plus tard pour la prod
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='employes')
    score_fiabilite = models.FloatField(default=100.0)  # sur 100
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.site.nom})"


class Coupure(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='coupures')
    debut = models.DateTimeField()
    fin = models.DateTimeField(null=True, blank=True)
    declare_par = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, related_name='coupures_declarees')

    @property
    def duree(self):
        if self.fin:
            return self.fin - self.debut
        return None

    def __str__(self):
        return f"Coupure {self.site.nom} - {self.debut.strftime('%d/%m/%Y %H:%M')}"


class GroupeSession(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='groupe_sessions')
    employe = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, related_name='groupe_sessions')
    demarrage = models.DateTimeField()
    arret = models.DateTimeField(null=True, blank=True)

    @property
    def duree_heures(self):
        if self.arret:
            delta = self.arret - self.demarrage
            return round(delta.total_seconds() / 3600, 2)
        return None

    def __str__(self):
        return f"Session groupe {self.site.nom} - {self.demarrage.strftime('%d/%m/%Y %H:%M')}"


class PleinCarburant(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='pleins_carburant')
    employe = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, related_name='pleins_carburant')
    litres = models.FloatField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()

    def __str__(self):
        return f"Plein {self.litres}L - {self.site.nom} - {self.date.strftime('%d/%m/%Y')}"


class ConsommationElectricite(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='consommations')
    mois = models.DateField()  # on stocke le 1er jour du mois concerné
    kwh = models.FloatField(null=True, blank=True)
    montant_facture = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('site', 'mois')

    def __str__(self):
        return f"{self.site.nom} - {self.mois.strftime('%m/%Y')}"


class Alerte(models.Model):
    TYPE_CARBURANT = 'carburant'
    TYPE_ELECTRICITE = 'electricite'
    TYPE_CHOICES = [
        (TYPE_CARBURANT, 'Écart carburant'),
        (TYPE_ELECTRICITE, 'Écart consommation électrique'),
    ]

    type_alerte = models.CharField(max_length=20, choices=TYPE_CHOICES)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='alertes')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    resolue = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.type_alerte}] {self.site.nom} - {'Résolue' if self.resolue else 'Active'}"