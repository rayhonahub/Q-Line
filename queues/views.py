from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import httpx
import logging

from .models import Queue, Ticket
from .serializers import (
    QueueSerializer, TicketSerializer,
    TicketCreateSerializer, TicketDetailSerializer,
)
from accounts.models import User
from organizations.models import Organization, Branch
from accounts.permissions import IsStaff, IsOrgAdmin

logger = logging.getLogger(__name__)


# ─── Single, correct notification helper ───────────────────────────────────────

def send_telegram_notification(telegram_id: int, message: str) -> None:
    """
    Fire-and-forget sync HTTP call to Telegram Bot API.
    Wrapped in try/except — a failed notification must never break the main flow.
    """
    from django.conf import settings
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        with httpx.Client(timeout=5) as client:
            client.post(url, json={"chat_id": telegram_id, "text": message, "parse_mode": "HTML"})
    except Exception as exc:
        logger.warning("Telegram notification failed for %s: %s", telegram_id, exc)


# ─── Queue CRUD ────────────────────────────────────────────────────────────────

class QueueListCreateView(generics.ListCreateAPIView):
    serializer_class = QueueSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin]

    def get_queryset(self):
        branch_id = self.kwargs.get('branch_id')
        return Queue.objects.filter(branch_id=branch_id, is_active=True)

    def perform_create(self, serializer):
        branch = get_object_or_404(Branch, pk=self.kwargs['branch_id'])
        serializer.save(branch=branch)


class QueueDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QueueSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin]
    queryset = Queue.objects.all()


# ─── Ticket: Staff creates/calls/completes ─────────────────────────────────────

class TicketListView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsStaff]

    def get_queryset(self):
        queue_id = self.kwargs['queue_id']
        status_filter = self.request.query_params.get('status')
        qs = Ticket.objects.filter(queue_id=queue_id).select_related('customer', 'window')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class TicketCallView(APIView):
    """Staff calls the next waiting ticket at a window."""
    permission_classes = [IsAuthenticated, IsStaff]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id, status=Ticket.Status.WAITING)
        window_id = request.data.get('window_id')

        ticket.status = Ticket.Status.CALLED
        ticket.called_at = timezone.now()
        if window_id:
            from organizations.models import Window
            ticket.window_id = window_id
        ticket.save(update_fields=['status', 'called_at', 'window_id'])

        # Notify customer via Telegram
        if ticket.customer and ticket.customer.telegram_id:
            window_name = ticket.window.name if ticket.window else "—"
            msg = (
                f"📢 <b>Навбати шумо даъват шуд!</b>\n"
                f"🎫 Рақам: <b>{ticket.number}</b>\n"
                f"🪟 Тиреза: <b>{window_name}</b>\n"
                f"🕐 Вақт: {ticket.called_at.strftime('%H:%M')}"
            )
            send_telegram_notification(ticket.customer.telegram_id, msg)

        return Response(TicketSerializer(ticket).data)


class TicketCompleteView(APIView):
    """Staff marks a ticket as completed or no-show."""
    permission_classes = [IsAuthenticated, IsStaff]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(
            Ticket, pk=ticket_id, status__in=[Ticket.Status.CALLED, Ticket.Status.SERVING]
        )
        new_status = request.data.get('status', Ticket.Status.COMPLETED)
        if new_status not in (Ticket.Status.COMPLETED, Ticket.Status.NO_SHOW):
            return Response(
                {"detail": "status must be 'completed' or 'no_show'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.status = new_status
        ticket.completed_at = timezone.now()
        ticket.save(update_fields=['status', 'completed_at'])

        if ticket.customer and ticket.customer.telegram_id:
            if new_status == Ticket.Status.COMPLETED:
                msg = f"✅ Хизматрасонии шумо тамом шуд. Ташаккур!\n🎫 Рақам: {ticket.number}"
            else:
                msg = f"❌ Навбати шумо ({ticket.number}) бекор карда шуд — наомадед."
            send_telegram_notification(ticket.customer.telegram_id, msg)

        return Response(TicketSerializer(ticket).data)


class TicketCancelView(APIView):
    """Customer or staff cancels a waiting ticket."""
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)

        # Only the ticket owner or staff+ can cancel
        user = request.user
        is_staff = user.role in ('super_admin', 'org_admin', 'staff')
        if not is_staff and ticket.customer != user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if ticket.status not in (Ticket.Status.WAITING, Ticket.Status.CALLED):
            return Response(
                {"detail": "Only waiting or called tickets can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.status = Ticket.Status.CANCELLED
        ticket.save(update_fields=['status'])
        return Response({"detail": "Ticket cancelled."})


# ─── Telegram Bot → Backend: create ticket ────────────────────────────────────

class TelegramTicketCreateView(APIView):
    """
    Called exclusively by the Telegram bot (shared secret in header).
    Creates a ticket and notifies the customer + all staff of that branch.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Shared-secret auth — keeps this endpoint bot-only without JWT
        from django.conf import settings
        secret = request.headers.get('X-Bot-Secret', '')
        if secret != settings.TELEGRAM_BOT_SECRET:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        telegram_id = request.data.get('telegram_id')
        queue_id = request.data.get('queue_id')

        if not telegram_id or not queue_id:
            return Response(
                {"detail": "telegram_id and queue_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer = get_object_or_404(User, telegram_id=telegram_id)
        queue = get_object_or_404(Queue, pk=queue_id, is_active=True)

        # Prevent duplicate active tickets in the same queue
        existing = Ticket.objects.filter(
            queue=queue,
            customer=customer,
            status__in=[Ticket.Status.WAITING, Ticket.Status.CALLED, Ticket.Status.SERVING],
        ).first()
        if existing:
            return Response(
                {
                    "detail": "Шумо аллакай дар ин навбат ҳастед.",
                    "ticket_number": existing.number,
                    "position": self._get_position(existing),
                },
                status=status.HTTP_409_CONFLICT,
            )

        with transaction.atomic():
            ticket = self._create_ticket(queue, customer)

        position = self._get_position(ticket)
        now = timezone.localtime(ticket.created_at)

        # ── Notify customer ──
        customer_msg = (
            f"✅ <b>Навбат гирифта шуд!</b>\n"
            f"🏢 {queue.branch.organization.name} — {queue.branch.name}\n"
            f"📋 Навбат: {queue.name}\n"
            f"🎫 Рақами шумо: <b>{ticket.number}</b>\n"
            f"👥 Пеш аз шумо: <b>{position}</b> нафар\n"
            f"📅 Сана: {now.strftime('%d.%m.%Y')}\n"
            f"🕐 Вақт: {now.strftime('%H:%M')}"
        )
        send_telegram_notification(telegram_id, customer_msg)

        # ── Notify all staff of this branch ──
        self._notify_staff(queue, ticket, customer, now)

        return Response(
            {
                "ticket_number": ticket.number,
                "position": position,
                "queue": queue.name,
                "branch": queue.branch.name,
                "created_at": ticket.created_at,
            },
            status=status.HTTP_201_CREATED,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _generate_ticket_number(queue: Queue) -> str:
        """
        Resets daily: A001 on each new day.
        Uses select_for_update inside the caller's atomic block.
        """
        today = timezone.localdate()
        last = (
            Ticket.objects.select_for_update()
            .filter(queue=queue, created_at__date=today)
            .order_by('-created_at')
            .first()
        )
        if last:
            try:
                seq = int(last.number[len(queue.prefix):]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return f"{queue.prefix}{seq:03d}"

    def _create_ticket(self, queue: Queue, customer: User) -> Ticket:
        number = self._generate_ticket_number(queue)
        return Ticket.objects.create(
            queue=queue,
            customer=customer,
            number=number,
            status=Ticket.Status.WAITING,
        )

    @staticmethod
    def _get_position(ticket: Ticket) -> int:
        """Number of WAITING tickets created strictly before this one (excludes self)."""
        return Ticket.objects.filter(
            queue=ticket.queue,
            status=Ticket.Status.WAITING,
            created_at__lt=ticket.created_at,
        ).count()

    @staticmethod
    def _notify_staff(queue: Queue, ticket: Ticket, customer: User, now) -> None:
        """Send a notification to every staff member assigned to this branch."""
        staff_qs = User.objects.filter(
            role__in=['org_admin', 'staff'],
            windows__branch=queue.branch,
            telegram_id__isnull=False,
        ).distinct().values_list('telegram_id', flat=True)

        tg_username = f"@{customer.username}" if customer.username else "—"
        phone = customer.phone or "—"
        full_name = customer.get_full_name() or customer.username
        waiting_count = Ticket.objects.filter(
            queue=queue, status=Ticket.Status.WAITING
        ).count()

        admin_msg = (
            f"🆕 <b>Навбати нав қайд шуд!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏢 Ташкилот: {queue.branch.organization.name}\n"
            f"🏬 Шӯъба: {queue.branch.name}\n"
            f"📋 Навбат: {queue.name}\n"
            f"🎫 Рақам: <b>{ticket.number}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Ном: {full_name}\n"
            f"✈️ Telegram: {tg_username}\n"
            f"📱 Телефон: {phone}\n"
            f"🆔 Telegram ID: <code>{customer.telegram_id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 Сана: {now.strftime('%d.%m.%Y')}\n"
            f"🕐 Вақт: {now.strftime('%H:%M')}\n"
            f"👥 Ҳамаи интизорон: {waiting_count} нафар"
        )
        for tid in staff_qs:
            send_telegram_notification(tid, admin_msg)


# ─── Customer: check own ticket status ────────────────────────────────────────

class MyTicketStatusView(APIView):
    """Telegram bot polls this to show current ticket status to the customer."""
    permission_classes = [AllowAny]

    def get(self, request, ticket_number):
        from django.conf import settings
        secret = request.headers.get('X-Bot-Secret', '')
        if secret != settings.TELEGRAM_BOT_SECRET:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        telegram_id = request.query_params.get('telegram_id')
        ticket = get_object_or_404(
            Ticket,
            number=ticket_number,
            customer__telegram_id=telegram_id,
        )
        position = TelegramTicketCreateView._get_position(ticket) if ticket.status == Ticket.Status.WAITING else 0
        return Response({
            "id": ticket.id,
            "number": ticket.number,
            "status": ticket.status,
            "position": position,
            "window": ticket.window.name if ticket.window else None,
            "called_at": ticket.called_at,
        })


# ─── Public: bot-facing queue list (no auth) ──────────────────────────────────

class PublicQueueListView(generics.ListAPIView):
    """
    No auth required — used by the Telegram bot to list active queues.
    Read-only, returns only active queues for a branch.
    """
    serializer_class = QueueSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Queue.objects.filter(
            branch_id=self.kwargs['branch_id'],
            is_active=True,
        )


# ─── Telegram: list active tickets for a user ─────────────────────────────────

class TelegramMyTicketsView(APIView):
    """
    Returns all active (waiting/called/serving) tickets for a given telegram_id.
    Called by the bot's start handler to show current queue status.
    """
    permission_classes = [AllowAny]

    def get(self, request, telegram_id):
        from django.conf import settings
        expected = getattr(settings, 'TELEGRAM_BOT_SECRET', '')
        secret = request.headers.get('X-Bot-Secret', '')
        if expected and secret != expected:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        tickets = Ticket.objects.filter(
            customer__telegram_id=telegram_id,
            status__in=[Ticket.Status.WAITING, Ticket.Status.CALLED, Ticket.Status.SERVING],
        ).select_related('queue', 'queue__branch', 'queue__branch__organization', 'window')

        data = [
            {
                "id": t.id,
                "number": t.number,
                "status": t.status,
                "queue": t.queue.name,
                "branch": t.queue.branch.name,
                "organization": t.queue.branch.organization.name,
                "position": TelegramTicketCreateView._get_position(t) if t.status == Ticket.Status.WAITING else 0,
                "window": t.window.name if t.window else None,
                "created_at": t.created_at,
            }
            for t in tickets
        ]
        return Response(data)