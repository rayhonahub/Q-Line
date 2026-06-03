from django.db import models
from accounts.models import User
from organizations.models import Branch, Window


class Queue(models.Model):
    branch      = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='queues')
    name        = models.CharField(max_length=255)  # "Умумӣ", "VIP", "Духтур А"
    prefix      = models.CharField(max_length=5, default='A')  # A001, B002...
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.branch.name} — {self.name}"


class Ticket(models.Model):
    class Status(models.TextChoices):
        WAITING   = 'waiting',   'Интизор'
        CALLED    = 'called',    'Даъват шуд'
        SERVING   = 'serving',   'Хизматрасонӣ'
        COMPLETED = 'completed', 'Тамом'
        CANCELLED = 'cancelled', 'Рад шуд'
        NO_SHOW   = 'no_show',   'Наомад'

    queue        = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='tickets')
    window       = models.ForeignKey(Window, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    customer     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    number       = models.CharField(max_length=10)   # A001, A002...
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    rating       = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    note         = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    called_at    = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.number} — {self.status}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Тасдиқ дар интизор'
        CONFIRMED = 'confirmed', 'Тасдиқ шуд'
        CANCELLED = 'cancelled', 'Рад шуд'
        DONE      = 'done',      'Тамом'

    queue        = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='appointments')
    customer     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    scheduled_at = models.DateTimeField()
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    note         = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} — {self.scheduled_at}"