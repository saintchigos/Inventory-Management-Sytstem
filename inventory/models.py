from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StockMovement(models.Model):

    MOVEMENT_CHOICES = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    )

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_CHOICES)
    quantity = models.PositiveIntegerField()
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.movement_type}"


class InventoryAuditLog(models.Model):

    ACTION_CHOICES = (
        ('CREATED', 'Created'),
        ('EDITED', 'Edited'),
        ('DELETED', 'Deleted'),
    )

    item_name = models.CharField(max_length=200)

    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES
    )

    details = models.TextField(
        blank=True,
        null=True
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} - {self.action}"