# queues/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ticket
from .tasks import notify_telegram  # Celery task


@receiver(post_save, sender=Ticket)
def ticket_status_changed(sender, instance, **kwargs):
    if not instance.tracker.has_changed('status'):
        return

    # Муштарии telegram_id дорад?
    if not instance.customer or not instance.customer.telegram_id:
        return

    # Ҳолат иваз шуд → хабар фирист
    if instance.status == 'called':
        notify_telegram.delay(instance.id, 'called')

    elif instance.status == 'completed':
        notify_telegram.delay(instance.id, 'completed')


# queues/tasks.py — Celery
from celery import shared_task
import httpx


@shared_task
def notify_telegram(ticket_id, event):
    from .models import Ticket
    ticket = Ticket.objects.select_related(
        'customer', 'window', 'queue__branch__organization'
    ).get(id=ticket_id)

    telegram_id = ticket.customer.telegram_id
    
    if event == 'called':
        text = (
            f"🔔 *Навбати шумо даъват шуд!*\n\n"
            f"🎫 Рақам: *{ticket.number}*\n"
            f"🪟 Кабинет: *{ticket.window.name}*\n"
            f"🏢 {ticket.queue.branch.organization.name}\n\n"
            f"Илтимос тезтар биёед!"
        )
    elif event == 'completed':
        text = (
            f"✅ *Хизматрасонӣ тамом шуд!*\n"
            f"Хизматро баҳо диҳед 👇"
        )

    # Telegram API
    httpx.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": telegram_id,
            "text": text,
            "parse_mode": "Markdown"
        }
    )