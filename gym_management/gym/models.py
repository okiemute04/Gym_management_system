from django.db import models
from django.contrib.auth.models import User


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('outstanding', 'Outstanding'),
        ('paid', 'Paid'),
        ('void', 'Void'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='invoices')
    date = models.DateField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Invoice #{self.pk}"


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = 0.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description}"


class Membership(models.Model):
    STATE_CHOICES = (
        ('active', 'Active'),
        ('canceled', 'Canceled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    state = models.CharField(choices=STATE_CHOICES, max_length=20)
    credits = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    invoices = models.ManyToManyField(Invoice, blank=True, related_name='memberships')


    def __str__(self):
        return f"Membership #{self.id}"


class Checkin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='checkins')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Checkin for {self.user.username} on {self.timestamp.date()}'

