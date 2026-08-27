import uuid
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Base model with UUID PK and audit timestamps."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_creation = models.DateTimeField(default=timezone.now, editable=False)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Site(BaseModel):
    """Site CAMTEL (siège, antenne, bâtiment annexe)."""

    class TypeCarburant(models.TextChoices):
        ESSENCE = 'essence', 'Essence'
        GAZOIL = 'gazoil', 'Gazoil'

    nom = models.CharField(max_length=255, unique=True)
    adresse = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    type_carburant = models.CharField(
        max_length=10,
        choices=TypeCarburant.choices,
        default=TypeCarburant.ESSENCE,
    )
    type_groupe = models.CharField(max_length=100, null=True, blank=True)
    puissance_kva = models.FloatField(null=True, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Site'
        verbose_name_plural = 'Sites'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Employe(BaseModel):
    """Employé terrain ou administratrice."""

    class Role(models.TextChoices):
        EMPLOYE = 'employe', 'Employé'
        ADMINISTRATRICE = 'administratrice', 'Administratrice'

    site = models.ForeignKey(
        Site,
        on_delete=models.RESTRICT,
        related_name='employes',
        null=True,
        blank=True,  # NULL pour administratrice (accès global)
        help_text="Site affecté (1 site par employé). NULL pour administratrice.",
    )
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    pin_hash = models.CharField(max_length=255, blank=True, default='')
    pin_salt = models.CharField(max_length=255, blank=True, default='')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYE)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    telegram_user_id = models.BigIntegerField(null=True, blank=True)
    date_embauche = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def set_pin(self, plain_pin):
        """Hache et stocke le PIN sécurisé (bcrypt)."""
        import bcrypt
        self.pin_salt = bcrypt.gensalt(rounds=12).decode()
        self.pin_hash = bcrypt.hashpw(
            plain_pin.encode('utf-8'),
            self.pin_salt.encode('utf-8'),
        ).decode()

    def verify_pin(self, plain_pin):
        """Vérifie un PIN en entrée."""
        import bcrypt
        if not self.pin_hash:
            return False
        try:
            return bcrypt.checkpw(
                plain_pin.encode('utf-8'), self.pin_hash.encode('utf-8'))
        except ValueError:
            return False

    @property
    def is_authenticated(self):
        """
        Requis par DRF/Django : l'authentification JWT personnalisée
        résout les tokens vers une instance Employe.
        """
        return self.actif

    @property
    def is_anonymous(self):
        return False


class Coupure(BaseModel):
    """Coupure d'électricité déclarée sur un site."""

    class Statut(models.TextChoices):
        OUVERTE = 'ouverte', 'Ouverte'
        FERMEE = 'fermee', 'Fermée'

    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='coupures')
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField(null=True, blank=True)
    duree_heures = models.FloatField(null=True, blank=True)
    employe_id_declaration = models.ForeignKey(
        Employe,
        on_delete=models.RESTRICT,
        related_name='coupures_declarees',
    )
    cause_descriptif = models.TextField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.OUVERTE)

    class Meta:
        verbose_name = 'Coupure'
        verbose_name_plural = 'Coupures'
        ordering = ['-date_debut']
        indexes = [
            models.Index(fields=['site', 'statut']),
        ]

    def __str__(self):
        return f"Coupure {self.site.nom} - {self.date_debut:%d/%m/%Y %H:%M}"


class SessionGroupe(BaseModel):
    """Session de fonctionnement d'un groupe électrogène."""

    class Statut(models.TextChoices):
        EN_COURS = 'en_cours', 'En cours'
        FERMEE = 'fermee', 'Fermée'

    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='sessions_groupe')
    timestamp_debut = models.DateTimeField()
    timestamp_fin = models.DateTimeField(null=True, blank=True)
    duree_heures = models.FloatField(null=True, blank=True)
    employe_id_declaration = models.ForeignKey(
        Employe,
        on_delete=models.RESTRICT,
        related_name='sessions_groupe_declarees',
    )
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.EN_COURS)

    class Meta:
        verbose_name = 'Session Groupe'
        verbose_name_plural = 'Sessions Groupe'
        ordering = ['-timestamp_debut']
        indexes = [
            models.Index(fields=['site', 'statut']),
        ]

    def __str__(self):
        return f"Session groupe {self.site.nom} - {self.timestamp_debut:%d/%m/%Y %H:%M}"


class PleineCarburant(BaseModel):
    """Plein de carburant enregistré."""

    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='pleins_carburant')
    quantite_litres = models.FloatField()
    prix_unitaire_fcfa = models.FloatField()
    montant_total_fcfa = models.FloatField(editable=False)
    date_plein = models.DateField()
    employe_id_declaration = models.ForeignKey(
        Employe,
        on_delete=models.RESTRICT,
        related_name='pleins_carburant_declares',
    )

    class Meta:
        verbose_name = 'Plein Carburant'
        verbose_name_plural = 'Pleins Carburant'
        ordering = ['-date_plein']
        indexes = [
            models.Index(fields=['site', 'date_plein']),
        ]

    def save(self, *args, **kwargs):
        self.montant_total_fcfa = self.quantite_litres * self.prix_unitaire_fcfa
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Plein {self.quantite_litres}L - {self.site.nom} - {self.date_plein:%d/%m/%Y}"


class ConsommationElectrique(BaseModel):
    """Consommation électrique mensuelle d'un site."""

    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='consommations_electriques')
    mois_annee = models.DateField()  # 1er jour du mois
    consommation_kwh = models.FloatField(null=True, blank=True)
    montant_facture_fcfa = models.FloatField(null=True, blank=True)
    employe_id_declarant = models.ForeignKey(
        Employe,
        on_delete=models.RESTRICT,
        related_name='consommations_electriques_declarees',
    )

    class Meta:
        verbose_name = 'Consommation Électrique'
        verbose_name_plural = 'Consommations Électriques'
        ordering = ['-mois_annee']
        constraints = [
            models.UniqueConstraint(fields=['site', 'mois_annee'], name='unique_site_mois'),
        ]
        indexes = [
            models.Index(fields=['site', 'mois_annee']),
        ]

    def __str__(self):
        return f"{self.site.nom} - {self.mois_annee:%m/%Y}"


class CalculRatioCarburant(BaseModel):
    """Ratio de consommation carburant calculé (L/h)."""

    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='ratios_carburant')
    mois_annee = models.DateField()  # 1er jour du mois
    ratio_litres_par_heure = models.FloatField()
    total_litres_periode = models.FloatField()
    total_heures_groupe = models.FloatField()
    nombre_pleins_periode = models.IntegerField()
    nombre_sessions_groupe = models.IntegerField()
    donnees_suffisantes = models.BooleanField(default=True)
    notes_calcul = models.TextField(null=True, blank=True)
    timestamp_calcul = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Calcul Ratio Carburant'
        verbose_name_plural = 'Calculs Ratio Carburant'
        ordering = ['-mois_annee']
        constraints = [
            models.UniqueConstraint(fields=['site', 'mois_annee'], name='unique_ratio_site_mois'),
        ]

    def __str__(self):
        return f"Ratio {self.site.nom} {self.mois_annee:%m/%Y}: {self.ratio_litres_par_heure} L/h"


class SeuillAlerte(models.Model):
    """Table singleton : seuils d'alerte globaux."""

    seuil_carburant_pct = models.FloatField(default=20.0)
    seuil_electricite_pct = models.FloatField(default=30.0)
    fenetre_historique_carburant_mois = models.IntegerField(default=6)
    fenetre_historique_electricite_mois = models.IntegerField(default=3)
    date_modification = models.DateTimeField(auto_now=True)
    modifie_par = models.ForeignKey(
        Employe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seuils_modifies',
    )

    class Meta:
        verbose_name = 'Seuil Alerte'
        verbose_name_plural = 'Seuils Alerte'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Seuils: carburant ±{self.seuil_carburant_pct}%, électricité ±{self.seuil_electricite_pct}%"


class Alerte(BaseModel):
    """Alerte générée suite à une anomalie détectée."""

    class TypeAlerte(models.TextChoices):
        CARBURANT = 'carburant_anomalie', 'Anomalie carburant'
        ELECTRICITE = 'electricite_anomalie', 'Anomalie électricité'

    class Severite(models.TextChoices):
        BAS = 'bas', 'Bas'
        MOYEN = 'moyen', 'Moyen'
        HAUT = 'haut', 'Haut'

    class Statut(models.TextChoices):
        ACTIF = 'actif', 'Actif'
        RESOLU = 'resolu', 'Résolu'
        IGNOREE = 'ignoree', 'Ignorée'

    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='alertes')
    type_alerte = models.CharField(max_length=30, choices=TypeAlerte.choices)
    severite = models.CharField(max_length=10, choices=Severite.choices, default=Severite.MOYEN)
    motif_technique = models.TextField()
    valeur_detectee = models.FloatField()
    valeur_seuil = models.FloatField()
    employe_id_lien = models.ForeignKey(
        Employe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes_liees',
    )
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.ACTIF)
    resolution_type = models.CharField(max_length=100, null=True, blank=True)
    resolution_note = models.TextField(null=True, blank=True)
    resolu_par = models.ForeignKey(
        Employe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes_resolues',
    )
    date_resolution = models.DateTimeField(null=True, blank=True)
    timestamp_creation = models.DateTimeField(default=timezone.now)
    telegram_notification_sent = models.BooleanField(default=False)
    telegram_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Alerte'
        verbose_name_plural = 'Alertes'
        ordering = ['-timestamp_creation']
        indexes = [
            models.Index(fields=['site', 'statut', 'type_alerte']),
            models.Index(fields=['-timestamp_creation']),
        ]

    def __str__(self):
        return f"[{self.type_alerte}] {self.site.nom} - {self.statut}"


class ScoreFiabiliteEmploye(BaseModel):
    """Score de fiabilité mensuel d'un employé."""

    employe = models.ForeignKey(Employe, on_delete=models.RESTRICT, related_name='scores_fiabilite')
    mois_annee = models.DateField()  # 1er jour du mois
    score_base = models.IntegerField(default=100)
    total_penalites = models.IntegerField(default=0)
    score_final = models.IntegerField()
    detail_penalites = models.JSONField(null=True, blank=True)
    nombre_operations_mois = models.IntegerField()
    date_calcul = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Score Fiabilité Employé'
        verbose_name_plural = 'Scores Fiabilité Employés'
        ordering = ['-mois_annee']
        constraints = [
            models.UniqueConstraint(fields=['employe', 'mois_annee'], name='unique_score_employe_mois'),
        ]

    def __str__(self):
        return f"{self.employe} - {self.mois_annee:%m/%Y}: {self.score_final}/100"


class AuditTrail(BaseModel):
    """Journalisation complète des opérations."""

    timestamp = models.DateTimeField(default=timezone.now)
    employe = models.ForeignKey(
        Employe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_trails',
    )
    action = models.CharField(max_length=100)
    table_cible = models.CharField(max_length=100)
    record_id = models.UUIDField(null=True, blank=True)
    donnees_avant = models.JSONField(null=True, blank=True)
    donnees_apres = models.JSONField(null=True, blank=True)
    adresse_ip = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Audit Trail'
        verbose_name_plural = 'Audit Trails'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.table_cible} - {self.timestamp}"