from django.urls import path
from .views import (
    QueueListCreateView,
    QueueDetailView,
    PublicQueueListView,
    TicketListView,
    TicketCallView,
    TicketCompleteView,
    TicketCancelView,
    TelegramTicketCreateView,
    TelegramMyTicketsView,
    MyTicketStatusView,
)

# Root is api/queues/ — do NOT prefix paths with 'queues/' again
urlpatterns = [
    # ── Public (bot-facing, no auth) ─────────────────────────────────────────
    # GET  /api/queues/branches/<id>/queues/
    path('branches/<int:branch_id>/queues/', PublicQueueListView.as_view(), name='queue-list-public'),

    # ── Queue management (admin only) ─────────────────────────────────────────
    # GET/POST  /api/queues/branches/<id>/queues/manage/
    path('branches/<int:branch_id>/queues/manage/', QueueListCreateView.as_view(), name='queue-list-create'),
    # GET/PUT/DELETE  /api/queues/<id>/
    path('<int:pk>/', QueueDetailView.as_view(), name='queue-detail'),

    # ── Ticket management (staff) ─────────────────────────────────────────────
    # GET  /api/queues/<id>/tickets/
    path('<int:queue_id>/tickets/', TicketListView.as_view(), name='ticket-list'),
    # POST /api/queues/tickets/<id>/call/
    path('tickets/<int:ticket_id>/call/', TicketCallView.as_view(), name='ticket-call'),
    # POST /api/queues/tickets/<id>/complete/
    path('tickets/<int:ticket_id>/complete/', TicketCompleteView.as_view(), name='ticket-complete'),
    # POST /api/queues/tickets/<id>/cancel/
    path('tickets/<int:ticket_id>/cancel/', TicketCancelView.as_view(), name='ticket-cancel'),

    # ── Telegram bot endpoints (X-Bot-Secret auth) ────────────────────────────
    # POST /api/queues/telegram/join/
    path('telegram/join/', TelegramTicketCreateView.as_view(), name='telegram-ticket-join'),
    # GET  /api/queues/telegram/ticket/<number>/status/
    path('telegram/ticket/<str:ticket_number>/status/', MyTicketStatusView.as_view(), name='telegram-ticket-status'),
    # GET  /api/queues/tickets/telegram/<telegram_id>/
    path('tickets/telegram/<int:telegram_id>/', TelegramMyTicketsView.as_view(), name='telegram-my-tickets'),
]