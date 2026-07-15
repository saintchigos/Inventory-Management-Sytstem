from django import forms
from django.forms import modelformset_factory
from .models import ProcurementRequest
from .models import Quotation


class ProcurementRequestForm(forms.ModelForm):

    class Meta:
        model = ProcurementRequest

        fields = ['item', 'new_item_name', 'requested_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].required = False
        self.fields['new_item_name'].required = False
        self.fields['new_item_name'].help_text = "Only fill this in if the item isn't listed above."

    def clean(self):
        cleaned_data = super().clean()

        item = cleaned_data.get('item')
        new_item_name = cleaned_data.get('new_item_name')

        if not item and not new_item_name:
            raise forms.ValidationError(
                "Select an existing item, or type a name for a new item."
            )

        if item and new_item_name:
            raise forms.ValidationError(
                "Choose only one: either select an existing item, or type a new one, not both."
            )

        return cleaned_data


class QuotationForm(forms.ModelForm):

    class Meta:
        model = Quotation

        fields = ['vendor_name', 'price', 'document']


QuotationFormSet = modelformset_factory(
    Quotation,
    form=QuotationForm,
    extra=3,
    max_num=3
)


class PaymentProofForm(forms.ModelForm):

    class Meta:
        model = ProcurementRequest

        fields = ['payment_proof']


class LinkItemForm(forms.ModelForm):

    class Meta:
        model = ProcurementRequest

        fields = ['item']