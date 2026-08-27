from datetime import date, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone
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
)


class CalculateurRatioCarburant:
    """Calcule le ratio de consommation carburant (L/h) pour un site et un mois."""

    @staticmethod
    def mois_premier_jour(mois_annee):
        """Normalise une date au 1er jour du mois."""
        if isinstance(mois_annee, date):
            return mois_annee.replace(day=1)
        return mois_annee

    def calculer(self, site_id, mois_annee):
        """Calcule le ratio pour un site donné et un mois donné."""
        mois_annee = self.mois_premier_jour(mois_annee)
        mois_suivant = (mois_annee + timedelta(days=32)).replace(day=1)

        # Total litres enregistrés dans le mois
        pleins = PleineCarburant.objects.filter(
            site_id=site_id,
            date_plein__gte=mois_annee,
            date_plein__lt=mois_suivant,
        )
        total_litres = pleins.aggregate(total=Sum('quantite_litres'))['total'] or 0
        nombre_pleins = pleins.count()

        # Total heures groupe dans le mois
        sessions = SessionGroupe.objects.filter(
            site_id=site_id,
            timestamp_debut__gte=mois_annee,
            timestamp_debut__lt=mois_suivant,
            statut='fermee',
        )
        total_heures = sessions.aggregate(total=Sum('duree_heures'))['total'] or 0
        nombre_sessions = sessions.count()

        # Vérifier données suffisantes
        donnees_suffisantes = (
            total_heures > 0
            and nombre_sessions >= 2
            and nombre_pleins >= 1
        )

        notes = None
        if not donnees_suffisantes:
            if total_heures <= 0:
                notes = f"Données partielles: {nombre_sessions} sessions groupe"
            elif nombre_sessions < 2:
                notes = f"Données partielles: {nombre_sessions} session(s) seulement"
            elif nombre_pleins < 1:
                notes = f"Données partielles: {nombre_pleins} plein(s) seulement"

        # Pas de calcul trompeur : données insuffisantes → ne pas créer de ratio
        if not donnees_suffisantes or total_heures <= 0:
            return None

        ratio = total_litres / total_heures

        obj, created = CalculRatioCarburant.objects.update_or_create(
            site_id=site_id,
            mois_annee=mois_annee,
            defaults={
                'ratio_litres_par_heure': round(ratio, 2),
                'total_litres_periode': total_litres,
                'total_heures_groupe': round(total_heures, 2),
                'nombre_pleins_periode': nombre_pleins,
                'nombre_sessions_groupe': nombre_sessions,
                'donnees_suffisantes': donnees_suffisantes,
                'notes_calcul': notes,
                'timestamp_calcul': timezone.now(),
            },
        )
        return obj

    def recalculer_tous_sites(self, mois=None):
        """Recalcule les ratios pour tous les sites actifs pour un mois donné."""
        if mois is None:
            mois = timezone.now().date().replace(day=1)
        else:
            mois = self.mois_premier_jour(mois)

        results = []
        for site in Site.objects.filter(actif=True):
            obj = self.calculer(site_id=site.id, mois_annee=mois)
            if obj:
                results.append(obj)
        return results


class DetecteurAnomalieCarburant:
    """Détecte les anomalies de consommation carburant."""

    def detecter(self, site_id=None, mois=None):
        """
        Détecte les anomalies carburant pour un site (ou tous) pour un mois (ou le mois courant).
        """
        try:
            from .tasks.notifications import envoyer_alerte_telegram
        except ImportError:
            envoyer_alerte_telegram = None

        if mois is None:
            mois = timezone.now().date().replace(day=1)
        else:
            mois = mois.replace(day=1) if isinstance(mois, date) else mois

        seuils = SeuillAlerte.get_solo()
        fenetre = seuils.fenetre_historique_carburant_mois
        seuil_pct = seuils.seuil_carburant_pct

        sites = Site.objects.filter(actif=True)
        if site_id:
            sites = sites.filter(pk=site_id)

        alertes_crees = []

        for site in sites:
            # Ratio du mois en cours
            ratio = CalculRatioCarburant.objects.filter(
                site=site,
                mois_annee=mois,
                donnees_suffisantes=True,
            ).first()

            if not ratio:
                continue  # Données insuffisantes → pas d'alerte (Règle 7)

            # Moyenne historique sur fenêtre
            debut_fenetre = (mois - timedelta(days=32 * fenetre)).replace(day=1)
            ratios_historiques = CalculRatioCarburant.objects.filter(
                site=site,
                mois_annee__gte=debut_fenetre,
                mois_annee__lt=mois,
                donnees_suffisantes=True,
            ).values_list('ratio_litres_par_heure', flat=True)

            if not ratios_historiques:
                continue  # Pas de moyenne → pas d'alerte

            moyenne = sum(ratios_historiques) / len(ratios_historiques)
            if moyenne == 0:
                continue

            ratio_actuel = ratio.ratio_litres_par_heure
            ecart_pct = abs(ratio_actuel - moyenne) / moyenne * 100

            if ecart_pct > seuil_pct:
                # Créer l'alerte
                alerte = Alerte.objects.create(
                    site=site,
                    type_alerte=Alerte.TypeAlerte.CARBURANT,
                    severite=self._calculer_severite(ecart_pct, seuil_pct),
                    motif_technique=(
                        f"Ratio {ratio_actuel} L/h vs moyenne {moyenne:.2f} L/h, "
                        f"écart {ecart_pct:.1f}% (seuil {seuil_pct}%)"
                    ),
                    valeur_detectee=round(ecart_pct, 2),
                    valeur_seuil=seuil_pct,
                )
                alertes_crees.append(alerte)
                # Envoyer notification Telegram
                if envoyer_alerte_telegram:
                    envoyer_alerte_telegram.delay(alerte.id)

        return alertes_crees

    @staticmethod
    def _calculer_severite(ecart_pct, seuil_pct):
        if ecart_pct > seuil_pct * 2:
            return Alerte.Severite.HAUT
        elif ecart_pct > seuil_pct * 1.5:
            return Alerte.Severite.MOYEN
        return Alerte.Severite.BAS


class DetecteurAnomalieElectricite:
    """Détecte les anomalies de consommation électrique mensuelle."""

    def detecter(self, site_id=None, mois=None):
        """
        Détecte si la consommation électrique du mois M s'écarte > seuil de la moyenne des 3 mois précédents.
        """
        try:
            from .tasks.notifications import envoyer_alerte_telegram
        except ImportError:
            envoyer_alerte_telegram = None

        if mois is None:
            mois = timezone.now().date().replace(day=1)
        else:
            mois = mois.replace(day=1) if isinstance(mois, date) else mois

        seuils = SeuillAlerte.get_solo()
        fenetre = seuils.fenetre_historique_electricite_mois
        seuil_pct = seuils.seuil_electricite_pct

        sites = Site.objects.filter(actif=True)
        if site_id:
            sites = sites.filter(pk=site_id)

        alertes_crees = []

        for site in sites:
            conso_mois = ConsommationElectrique.objects.filter(
                site=site,
                mois_annee=mois,
            ).first()

            if not conso_mois or conso_mois.consommation_kwh is None:
                continue

            # Consommations des N mois précédents (complètement clos)
            debut = (mois - timedelta(days=32 * (fenetre + 1))).replace(day=1)
            conso_precedentes = list(
                ConsommationElectrique.objects.filter(
                    site=site,
                    mois_annee__gte=debut,
                    mois_annee__lt=mois,
                    consommation_kwh__isnull=False,
                ).order_by('-mois_annee')[:fenetre]
            )

            if len(conso_precedentes) < 2:
                continue  # Règle 7 : données insuffisantes

            moyenne = sum(c.consommation_kwh for c in conso_precedentes) / len(conso_precedentes)
            if moyenne == 0:
                continue

            conso_actuelle = conso_mois.consommation_kwh
            ecart_pct = abs(conso_actuelle - moyenne) / moyenne * 100

            if ecart_pct > seuil_pct:
                alerte = Alerte.objects.create(
                    site=site,
                    type_alerte=Alerte.TypeAlerte.ELECTRICITE,
                    severite=self._calculer_severite(ecart_pct, seuil_pct),
                    motif_technique=(
                        f"Consommation {conso_actuelle} kWh vs "
                        f"moyenne {moyenne:.2f} kWh (3 mois), écart {ecart_pct:.2f}% "
                        f"(seuil ±{seuil_pct}%)"
                    ),
                    valeur_detectee=round(ecart_pct, 2),
                    valeur_seuil=seuil_pct,
                    employe_id_lien=conso_mois.employe_id_declarant,
                )
                alertes_crees.append(alerte)
                if envoyer_alerte_telegram:
                    envoyer_alerte_telegram.delay(alerte.id)

        return alertes_crees

    @staticmethod
    def _calculer_severite(ecart_pct, seuil_pct):
        if ecart_pct > seuil_pct * 2:
            return Alerte.Severite.HAUT
        elif ecart_pct > seuil_pct * 1.5:
            return Alerte.Severite.MOYEN
        return Alerte.Severite.BAS


class CalculateurScoreFiabilite:
    """Calcule le score de fiabilité mensuel des employés."""

    PENALITES = {
        'anomalie_carburant': 5,
        'anomalie_electricite': 3,
        'coupure_non_fermee': 10,
        'operation_incoherente': 2,
    }

    def calculer_pour_mois(self, mois, employe_id=None):
        """
        Calcule le score de fiabilité pour le mois M-1 (ou le mois passé en paramètre).
        """
        mois_annee = mois.replace(day=1)

        employes = Employe.objects.filter(role='employe', actif=True)
        if employe_id:
            employes = employes.filter(pk=employe_id)

        scores = []

        for employe in employes:
            detail_penalites = {
                'anomalie_carburant': 0,
                'anomalie_electricite': 0,
                'coupure_non_fermee': 0,
                'operation_incoherente': 0,
            }

            # Opérations de l'employé pour le mois
            plein_count = PleineCarburant.objects.filter(
                employe_id_declaration=employe,
                date_plein__year=mois_annee.year,
                date_plein__month=mois_annee.month,
            ).count()

            coupure_count = Coupure.objects.filter(
                employe_id_declaration=employe,
                date_debut__year=mois_annee.year,
                date_debut__month=mois_annee.month,
            ).count()

            session_count = SessionGroupe.objects.filter(
                employe_id_declaration=employe,
                timestamp_debut__year=mois_annee.year,
                timestamp_debut__month=mois_annee.month,
            ).count()

            nombre_operations = plein_count + coupure_count + session_count

            # Règle 7 : si < 5 opérations → score "insuffisant"
            if nombre_operations < 5:
                score_obj, _ = ScoreFiabiliteEmploye.objects.update_or_create(
                    employe=employe,
                    mois_annee=mois_annee,
                    defaults={
                        'score_base': 100,
                        'total_penalites': 0,
                        'score_final': 100,
                        'detail_penalites': {'insuffisant': True},
                        'nombre_operations_mois': nombre_operations,
                        'date_calcul': timezone.now(),
                    },
                )
                scores.append(score_obj)
                continue

            # Pénalité : anomalies carburant liées à l'employé
            anomalies_carburant = Alerte.objects.filter(
                employe_id_lien=employe,
                type_alerte='carburant_anomalie',
                timestamp_creation__year=mois_annee.year,
                timestamp_creation__month=mois_annee.month,
            ).count()
            detail_penalites['anomalie_carburant'] = anomalies_carburant

            # Pénalité : anomalies électrique liées à l'employé
            anomalies_electricite = Alerte.objects.filter(
                employe_id_lien=employe,
                type_alerte='electricite_anomalie',
                timestamp_creation__year=mois_annee.year,
                timestamp_creation__month=mois_annee.month,
            ).count()
            detail_penalites['anomalie_electricite'] = anomalies_electricite

            # Pénalité : coupures non fermées > 48h
            coupures_non_fermees = Coupure.objects.filter(
                employe_id_declaration=employe,
                statut='fermee',
                date_fin__year=mois_annee.year,
                date_fin__month=mois_annee.month,
                duree_heures__gt=48,
            ).count()
            detail_penalites['coupure_non_fermee'] = coupures_non_fermees

            total_penalites = (
                anomalies_carburant * self.PENALITES['anomalie_carburant']
                + anomalies_electricite * self.PENALITES['anomalie_electricite']
                + coupures_non_fermees * self.PENALITES['coupure_non_fermee']
            )
            # Ne pas aller sous 0
            score_final = max(0, 100 - total_penalites)

            score_obj, _ = ScoreFiabiliteEmploye.objects.update_or_create(
                employe=employe,
                mois_annee=mois_annee,
                defaults={
                    'score_base': 100,
                    'total_penalites': total_penalites,
                    'score_final': score_final,
                    'detail_penalites': detail_penalites,
                    'nombre_operations_mois': nombre_operations,
                    'date_calcul': timezone.now(),
                },
            )
            scores.append(score_obj)

        return scores