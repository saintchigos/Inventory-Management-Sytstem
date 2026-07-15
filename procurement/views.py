from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)
from .models import ProcurementRequest
from .models import Quotation
from .forms import ProcurementRequestForm
from .forms import QuotationForm
from .forms import QuotationFormSet
from .forms import LinkItemForm

from inventory.models import StockMovement

from users.permissions import (
    is_procurement,
    is_accounts,
    is_storesman
)


@login_required
@user_passes_test(is_procurement)
def procurement_list(request):

    requests = ProcurementRequest.objects.all().order_by('-created_at')

    return render(request, 'procurement/procurement_list.html', {
        'requests': requests
    })


@login_required
@user_passes_test(is_procurement)
def create_procurement_request(request):

    if request.method == 'POST':

        form = ProcurementRequestForm(request.POST)

        if form.is_valid():

            procurement = form.save(commit=False)

            procurement.requested_by = request.user

            procurement.save()

            return redirect('procurement_list')

    else:
        initial_data = {}

        item_id = request.GET.get('item')

        if item_id:
            initial_data['item'] = item_id

        form = ProcurementRequestForm(initial=initial_data)

    return render(request, 'procurement/create_procurement.html', {
        'form': form
    })


@login_required
@user_passes_test(is_accounts)
def approve_request(request, request_id):

    procurement = get_object_or_404(
        ProcurementRequest,
        id=request_id
    )

    procurement.status = 'WAITING_PAYMENT'

    procurement.accounts_approved_by = request.user

    procurement.save()

    return redirect('request_detail', request_id=request_id)


@login_required
@user_passes_test(is_accounts)
def reject_request(request, request_id):

    procurement = get_object_or_404(
        ProcurementRequest,
        id=request_id
    )

    procurement.status = 'REJECTED'

    procurement.accounts_approved_by = request.user

    procurement.save()

    return redirect('accounts_dashboard')


@login_required
@user_passes_test(is_storesman)
def storesman_dashboard(request):

    approved_requests = ProcurementRequest.objects.filter(
        status='PAYMENT_RECEIVED'
    ).order_by('-created_at')

    return render(request, 'procurement/storesman_dashboard.html', {
        'approved_requests': approved_requests
    })


@login_required
@user_passes_test(is_storesman)
def link_item(request, request_id):

    procurement = get_object_or_404(
        ProcurementRequest,
        id=request_id
    )

    if request.method == 'POST':

        form = LinkItemForm(request.POST, instance=procurement)

        if form.is_valid():

            form.save()

            return redirect('delivery_dashboard')

    else:
        form = LinkItemForm(instance=procurement)

    return render(request, 'procurement/link_item.html', {
        'form': form,
        'procurement': procurement
    })


@login_required
@user_passes_test(is_storesman)
def confirm_delivery(request, request_id):

    procurement = get_object_or_404(
        ProcurementRequest,
        id=request_id
    )

    if not procurement.item:
        return redirect('link_item', request_id=request_id)

    item = procurement.item

    item.quantity += procurement.requested_quantity

    item.save()

    procurement.status = 'DELIVERED'

    procurement.save()

    # Create stock movement
    StockMovement.objects.create(
        item=item,
        movement_type='IN',
        quantity=procurement.requested_quantity,
        performed_by=request.user
    )

    return redirect('delivery_dashboard')


@login_required
@user_passes_test(is_procurement)
def add_quotation(request, request_id):

    procurement = get_object_or_404(
        ProcurementRequest,
        id=request_id
    )

    if request.method == 'POST':

        formset = QuotationFormSet(
            request.POST,
            request.FILES,
            queryset=Quotation.objects.none()
        )

        selected_index = request.POST.get('selected_index')

        if formset.is_valid() and selected_index is not None:

            saved_quotations = []

            for form in formset:
                quotation = form.save(commit=False)
                quotation.request = procurement
                quotation.uploaded_by = request.user
                quotation.save()
                saved_quotations.append(quotation)

            procurement.selected_quotation = saved_quotations[int(selected_index)]
            procurement.status = 'PENDING'
            procurement.save()

            return redirect('procurement_list')

    else:
        formset = QuotationFormSet(queryset=Quotation.objects.none())

    return render(request, 'procurement/add_quotation.html', {
        'formset': formset,
        'procurement': procurement
    })