from django import forms
from .models import Allocation


class AllocationForm(forms.ModelForm):

    class Meta:
        model = Allocation

        fields = [
            'item',
            'department',
            'quantity',
            'receiver_name',
            'notes',
        ]