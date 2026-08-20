from rest_framework import serializers
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


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = [
            'id',
            'nom',
            'adresse',
            'latitude',
            'longitude',
            'type_carburant',
            'type_groupe',
            'puissance_kva',
            'actif',
            'date_creation',
            'date_modification',
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']


class EmployeSerializer(serializers.ModelSerializer):
    site_nom = serializers.CharField(source='site.nom', read_only=True)

    class Meta:
        model = Employe
        fields = [
            'id',
            'site',
            'site_nom',
            'prenom',
            'nom',
            'email',
            'role',
            'telephone',
            'telegram_user_id',
            'date_embauche',
            'actif',
            'date_creation',
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']


class EmployeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création d'employé avec PIN."""

    pin = serializers.CharField(write_only=True, min_length=4, max_length=4)

    class Meta:
        model = Employe
        fields = [
            'id',
            'site',
            'prenom',
            'nom',
            'email',
            'role',
            'telephone',
            'telegram_user_id',
            'date_embauche',
            'pin',
        ]
        read_only_fields = ['id']

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Le PIN doit contenir uniquement des chiffres.")
        return value

    def create(self, validated_data):
        pin = validated_data.pop('pin')
        employe = Employe(**validated_data)
        employe.set_pin(pin)
        employe.save()
        return employe


class CoupureSerializer(serializers.ModelSerializer):
    site_nom = serializers.CharField(source='site.nom', read_only=True)

    class Meta:
        model = Coupure
        fields = [
            'id',
            'site',
            'site_nom',
            'date_debut',
            'date_fin',
            'duree_heures',
            'employe_id_declaration',
            'cause_descriptif',
            'statut',
            'date_creation',
        ]
        read_only_fields = ['id', 'duree_heures', 'employe_id_declaration', 'statut', 'date_creation']


class CoupureCloseSerializer(serializers.Serializer):
    date_fin = serializers.DateTimeField()

    def validate_date_fin(self, value):
        coupure = self.context['coupure']
        if value < coupure.date_debut:
            raise serializers.ValidationError("date_fin doit être postérieure à date_debut.")
        return value


class SessionGroupeSerializer(serializers.ModelSerializer):
    site_nom = serializers.CharField(source='site.nom', read_only=True)

    class Meta:
        model = SessionGroupe
        fields = [
            'id',
            'site',
            'site_nom',
            'timestamp_debut',
            'timestamp_fin',
            'duree_heures',
            'employe_id_declaration',
            'statut',
            'date_creation',
        ]
        read_only_fields = ['id', 'duree_heures', 'employe_id_declaration', 'statut', 'date_creation']


class SessionGroupeStopSerializer(serializers.Serializer):
    timestamp_fin = serializers.DateTimeField()

    def validate_timestamp_fin(self, value):
        session = self.context['session']
        if value < session.timestamp_debut:
            raise serializers.ValidationError("timestamp_fin doit être postérieur à timestamp_debut.")
        return value


class PleineCarburantSerializer(serializers.ModelSerializer):
    site_nom = serializers.CharField(source='site.nom', read_only=True)

    class Meta:
        model = PleineCarburant
        fields = [
            'id',
            'site',
            'site_nom',
            'quantite_litres',
            'prix_unitaire_fcfa',
            'montant_total_fcfa',
            'date_plein',
            'employe_id_declaration',
            'date_creation',
        ]
        read_only_fields = ['id', 'montant_total_fcfa', 'employe_id_declaration', 'date_creation']

    def validate_quantite_litres(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité de litres doit être > 0.")
        return value

    def validate_prix_unitaire_fcfa(self, value):
        if value < 0:
            raise serializers.ValidationError("Le prix unitaire ne peut pas être négatif.")
        return value

    def validate_date_plein(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("La date du plein ne peut pas être dans le futur.")
        return value


class ConsommationElectriqueSerializer(serializers.ModelSerializer):
    site_nom = serializers.CharField(source='site.nom', read_only=True)

    class Meta:
        model = ConsommationElectrique
        fields = [
            'id',
            'site',
            'site_nom',
            'mois_annee',
            'consommation_kwh',
            'montant_facture_fcfa',
            'employe_id_declarant',
            'date_creation',
        ]
        read_only_fields = ['id', 'employe_id_declarant', 'date_creation']

    def validate(self, attrs):
        mois = attrs.get('mois_annee')
        if mois:
            from django.utils import timezone
            now = timezone.now().date()
            if mois.month == now.month and mois.year == now.year:
                pass  # mois courant autorisé
            elif mois > now.replace(day=1):
                raise serializers.ValidationError({"mois_annee": "Le mois ne peut pas être dans le futur."})

        kwh = attrs.get('consommation_kwh')
        montant = attrs.get('montant_facture_fcfa')
        if kwh is None and montant is None:
            raise serializers.ValidationError(
                "Au moins une valeur requise : consommation_kwh ou montant_facture_fcfa."
            )
        return attrs


class CalculRatioCarburantSerializer(serializers.ModelSerializer):
    site_nom = serializers.CharField(source='site.nom', read_only=True)

    class Meta:
        model = CalculRatioCarburant
        fields = [
            'id',
            'site',
            'site_nom',
            'mois_annee',
            'ratio_litres_par_heure',
            'total_litres_periode',
            'total_heures_groupe',
            'nombre_pleins_periode',
            'nombre_sessions_groupe',
            'donnees_suffisantes',
            'notes_calcul',
            'timestamp_calcul',
        ]
        read_only_fields = '__all__'


class SeuillAlerteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeuillAlerte
        fields = [
            'seuil_carburant_pct',
            'seuil_electricite_pct',
            'fenetre_historique_carburant_mois',
            'fenetre_historique_electricite_mois',
            'date_modification',
        ]
        read_only_fields = ['date_modification']

    def validate_seuil_carburant_pct(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Le seuil doit être entre 0 et 100 %.")
        return value

    def validate_seuil_electricite_pct(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Le seuil doit être entre 0 et 100 %.")
        return value


class AlerteSerializer(serializers.ModelSerializer):
    site_nom = serializers.CharField(source='site.nom', read_only=True)
    employe_nom = serializers.CharField(
        source='employe_id_lien.nom',
        read_only=True,
        default=None,
    )

    class Meta:
        model = Alerte
        fields = [
            'id',
            'site',
            'site_nom',
            'type_alerte',
            'severite',
            'motif_technique',
            'valeur_detectee',
            'valeur_seuil',
            'employe_id_lien',
            'employe_nom',
            'statut',
            'resolution_type',
            'resolution_note',
            'resolu_par',
            'date_resolution',
            'timestamp_creation',
            'telegram_notification_sent',
            'telegram_timestamp',
        ]
        read_only_fields = '__all__'


class AlerteResolveSerializer(serializers.Serializer):
    resolution_type = serializers.ChoiceField(
        choices=[
            'fausse_alerte',
            'equipement_repare',
            'maintenance_prevue',
            'a_investiguer',
        ]
    )
    resolution_note = serializers.CharField(required=False, allow_blank=True)


class ScoreFiabiliteEmployeSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source='employe.nom', read_only=True)
    employe_prenom = serializers.CharField(source='employe.prenom', read_only=True)

    class Meta:
        model = ScoreFiabiliteEmploye
        fields = [
            'id',
            'employe',
            'employe_nom',
            'employe_prenom',
            'mois_annee',
            'score_base',
            'total_penalites',
            'score_final',
            'detail_penalites',
            'nombre_operations_mois',
            'date_calcul',
        ]
        read_only_fields = '__all__'


class AuditTrailSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source='employe.nom', read_only=True)

    class Meta:
        model = AuditTrail
        fields = [
            'id',
            'timestamp',
            'employe',
            'employe_nom',
            'action',
            'table_cible',
            'record_id',
            'donnees_avant',
            'donnees_apres',
            'adresse_ip',
            'user_agent',
        ]
        read_only_fields = '__all__'