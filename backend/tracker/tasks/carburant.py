from celery import shared_task
from django.utils import timezone
from ..services import CalculateurRatioCarburant


@shared_task
def calculer_ratio_carburant(site_id, mois_annee):
    """Tâche Celery : calcule le ratio carburant pour un site et un mois."""
    service = CalculateurRatioCarburant()
    return service.calculer(site_id=site_id, mois_annee=mois_annee)


@shared_task
def recalculer_tous_ratios(mois=None):
    """Tâche Celery : recalcule les ratios pour tous les sites actifs."""
    from datetime import date
    if mois is None:
        mois = timezone.now().date().replace(day=1)
    elif isinstance(mois, str):
        from datetime import datetime
        mois = datetime.strptime(mois, '%Y-%m-%d').date()

    service = CalculateurRatioCarburant()
    return service.recalculer_tous_sites(mois=mois)