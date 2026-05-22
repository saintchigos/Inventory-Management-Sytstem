from django.db import models
from django.conf import settings

from inventory.models import Item


class Department(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Allocation(models.Model):

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    allocated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    date_allocated = models.DateTimeField(auto_now_add=True)

    receiver_name = models.CharField(max_length=200)

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.item.name} -> {self.department.name}"