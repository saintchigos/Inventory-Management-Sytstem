from django import forms
from .models import ProcurementRequest


class ProcurementRequestForm(forms.ModelForm):

    class Meta:
        model = ProcurementRequest

        fields = ['item', 'requested_quantity']