from celery import shared_task
from django.utils import timezone
from ..services import CalculateurScoreFiabilite


@shared_task
def calculer_scores_fiabilite(mois=None):
    """Tâche Celery : calcule les scores de fiabilité pour le mois précédent."""
    from datetime import date

    if mois is None:
        # Mois précédent (M-1)
        today = timezone.now().date()
        mois = today.replace(day=1)
        # Mois précédent
        if mois.month == 1:
            mois = date(mois.year - 1, 12, 1)
        else:
            mois = date(mois.year, mois.month - 1, 1)
    elif isinstance(mois, str):
        from datetime import datetime
        mois = datetime.strptime(mois, '%Y-%m-%d').date()

    service = CalculateurScoreFiabilite()
    return service.calculer_pour_mois(mois=mois)