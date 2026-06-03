from rest_framework import serializers
from django.utils import timezone
from .models import Queue, Ticket, Appointment
from accounts.serializers import UserSerializer
from organizations.serializers import WindowSerializer


class QueueSerializer(serializers.ModelSerializer):
    waiting_count = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = ['id', 'branch', 'name', 'prefix', 'is_active', 'created_at', 'waiting_count']
        read_only_fields = ['created_at']

    def get_waiting_count(self, obj):
        return obj.tickets.filter(status=Ticket.Status.WAITING).count()


class TicketSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    window = WindowSerializer(read_only=True)
    position = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'queue', 'window', 'customer', 'number',
            'status', 'rating', 'note', 'position',
            'created_at', 'called_at', 'completed_at',
        ]
        read_only_fields = ['number', 'created_at', 'called_at', 'completed_at']

    def get_position(self, obj):
        """
        Returns the number of WAITING tickets strictly before this one.
        Returns None for non-waiting tickets (position is irrelevant).
        """
        if obj.status != Ticket.Status.WAITING:
            return None
        return Ticket.objects.filter(
            queue=obj.queue,
            status=Ticket.Status.WAITING,
            created_at__lt=obj.created_at,
        ).count()


class TicketDetailSerializer(TicketSerializer):
    """Extended serializer for single-ticket detail views."""
    class Meta(TicketSerializer.Meta):
        fields = TicketSerializer.Meta.fields + ['rating', 'note']


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Used by staff to manually create a ticket for a walk-in customer.
    Ticket numbering resets daily per queue.
    """
    class Meta:
        model = Ticket
        fields = ['queue', 'customer', 'note']

    def create(self, validated_data):
        queue = validated_data['queue']
        number = self._generate_number(queue)
        return Ticket.objects.create(
            number=number,
            status=Ticket.Status.WAITING,
            **validated_data,
        )

    @staticmethod
    def _generate_number(queue: Queue) -> str:
        today = timezone.localdate()
        last = (
            Ticket.objects.filter(queue=queue, created_at__date=today)
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


class TicketRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['rating', 'note']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def update(self, instance, validated_data):
        if instance.status != Ticket.Status.COMPLETED:
            raise serializers.ValidationError("Only completed tickets can be rated.")
        return super().update(instance, validated_data)


class AppointmentSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'queue', 'customer', 'scheduled_at', 'status', 'note', 'created_at']
        read_only_fields = ['created_at']