from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

from .models import ProcurementRequest
from .forms import ProcurementRequestForm

from inventory.models import StockMovement

from users.permissions import (
    is_procurement,
    is_accounts,
    is_storesman
)


@login_required
@user_passes_test(is_procurement)
def procurement_list(request):

    requests = ProcurementRequest.objects.all()

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
        form = ProcurementRequestForm()

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

    procurement.status = 'APPROVED'

    procurement.accounts_approved_by = request.user

    procurement.save()

    return redirect('procurement_list')


@login_required
@user_passes_test(is_storesman)
def confirm_delivery(request, request_id):

    procurement = get_object_or_404(
        ProcurementRequest,
        id=request_id
    )

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

    return redirect('procurement_list')