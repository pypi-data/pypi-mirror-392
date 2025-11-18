import logging

from django.dispatch import Signal, receiver

from lacrei_models.notification.services import NotificationService

logger = logging.getLogger(__name__)

notification = Signal()


@receiver(notification)
def send_notification(sender, template_prefix, email, context, recipient, **kwargs):
    """
    Escuta o sinal de notificação, tenta enviar o e-mail e, em caso de falha,
    loga o erro de forma apropriada e o relança para o Celery.
    """
    try:
        NotificationService.send(template_prefix, email, context, recipient)
    except Exception as e:
        logger.critical(
            f"FALHA CRÍTICA AO ENVIAR NOTIFICAÇÃO! Template: {template_prefix}, Erro: {e}",
            exc_info=True,
        )

        raise
