import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import requests

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
TELEGRAM_BOT_TOKEN_KEY = 'TELEGRAM_BOT_TOKEN'
TELEGRAM_ADMIN_CHAT_ID_KEY = 'TELEGRAM_ADMIN_CHAT_ID'


def envoyer_message_telegram(message, chat_id=None):
    """
    Envoie un message Telegram via l'API Bot.
    """
    token = getattr(settings, TELEGRAM_BOT_TOKEN_KEY, None)
    if chat_id is None:
        chat_id = getattr(settings, TELEGRAM_ADMIN_CHAT_ID_KEY, None)

    if not token or not chat_id:
        logger.warning("Telegram non configuré : token=%s chat_id=%s", bool(token), bool(chat_id))
        return False

    url = TELEGRAM_API_URL.format(token=token)
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("Message Telegram envoyé avec succès")
            return True
        else:
            logger.error("Échec envoi Telegram : %s %s", response.status_code, response.text)
            return False
    except requests.RequestException as e:
        logger.error("Erreur réseau Telegram : %s", e)
        return False


@shared_task
def envoyer_alerte_telegram(alerte_id):
    """
    Tâche Celery : envoie une notification Telegram d'alerte à l'administratrice.
    """
    from ..models import Alerte

    try:
        alerte = Alerte.objects.get(pk=alerte_id)
    except Alerte.DoesNotExist:
        logger.error("Alerte %s introuvable", alerte_id)
        return False

    if alerte.telegram_notification_sent:
        logger.info("Alerte %s déjà notifiée Telegram", alerte_id)
        return True

    type_label = "CARBURANT" if alerte.type_alerte == 'carburant_anomalie' else "ÉLECTRICITÉ"
    severite_icon = {
        'bas': 'ℹ️',
        'moyen': '⚠️',
        'haut': '🚨',
    }.get(alerte.severite, '⚠️')

    message = (
        f"{severite_icon} <b>ANOMALIE {type_label} DÉTECTÉE</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏢 <b>Site :</b> {alerte.site.nom}\n"
        f"📊 <b>Détail :</b> {alerte.motif_technique}\n"
        f"⚡ <b>Sévérité :</b> {alerte.severite}\n"
        f"🕐 <b>Détecté :</b> {alerte.timestamp_creation:%d/%m/%Y %H:%M}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Seuil appliqué : {alerte.valeur_seuil}%"
    )

    sent = envoyer_message_telegram(message)

    if sent:
        alerte.telegram_notification_sent = True
        alerte.telegram_timestamp = timezone.now()
        alerte.save(update_fields=['telegram_notification_sent', 'telegram_timestamp'])

    return sent