from celery import shared_task
from django.utils import timezone
from ..services import DetecteurAnomalieCarburant, DetecteurAnomalieElectricite


@shared_task
def detecter_anomalies_carburant(site_id=None, mois=None):
    """Tâche Celery : détecte les anomalies carburant."""
    if mois is None:
        mois = timezone.now().date().replace(day=1)
    elif isinstance(mois, str):
        from datetime import datetime
        mois = datetime.strptime(mois, '%Y-%m-%d').date()

    detecteur = DetecteurAnomalieCarburant()
    return detecteur.detecter(site_id=site_id, mois=mois)


@shared_task
def detecter_anomalies_electricite(site_id=None, mois=None):
    """Tâche Celery : détecte les anomalies électricité."""
    if mois is None:
        mois = timezone.now().date().replace(day=1)
    elif isinstance(mois, str):
        from datetime import datetime
        mois = datetime.strptime(mois, '%Y-%m-%d').date()

    detecteur = DetecteurAnomalieElectricite()
    return detecteur.detecter(site_id=site_id, mois=mois)