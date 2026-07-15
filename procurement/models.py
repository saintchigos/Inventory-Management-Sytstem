from django.db import models
from django.conf import settings
from inventory.models import Item


class ProcurementRequest(models.Model):

    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('WAITING_PAYMENT', 'Waiting for Payment'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('REJECTED', 'Rejected'),
        ('DELIVERED', 'Delivered'),
    )

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    new_item_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    requested_quantity = models.PositiveIntegerField()

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    accounts_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests'
    )

    selected_quotation = models.ForeignKey(
        'Quotation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )

    payment_proof = models.FileField(
        upload_to='payment_proofs/',
        null=True,
        blank=True
    )

    payment_confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_confirmations'
    )

    payment_received_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def display_name(self):
        if self.item:
            return self.item.name
        return self.new_item_name

    def __str__(self):
        return f"{self.display_name()} - {self.status}"


class Quotation(models.Model):

    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name='quotations'
    )

    vendor_name = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    document = models.FileField(upload_to='quotations/')

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor_name} - {self.price}"