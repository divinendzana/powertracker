# Import des tâches Celery (optionnel si celery non installé)
try:
    from .carburant import calculer_ratio_carburant, recalculer_tous_ratios
    from .alertes import detecter_anomalies_carburant, detecter_anomalies_electricite
    from .fiabilite import calculer_scores_fiabilite
    from .notifications import envoyer_alerte_telegram

    __all__ = [
        'calculer_ratio_carburant',
        'recalculer_tous_ratios',
        'detecter_anomalies_carburant',
        'detecter_anomalies_electricite',
        'calculer_scores_fiabilite',
        'envoyer_alerte_telegram',
    ]
except ImportError:
    # Celery non installé - les tâches asynchrones ne sont pas disponibles
    __all__ = []