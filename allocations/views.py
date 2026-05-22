from django.shortcuts import render, redirect
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

from .forms import AllocationForm
from .models import Allocation

from inventory.models import StockMovement

from users.permissions import is_storesman


@login_required
@user_passes_test(is_storesman)
def allocation_list(request):

    allocations = Allocation.objects.all().order_by(
        '-date_allocated'
    )

    return render(request, 'allocations/allocation_list.html', {
        'allocations': allocations
    })


@login_required
@user_passes_test(is_storesman)
def create_allocation(request):

    if request.method == 'POST':

        form = AllocationForm(request.POST)

        if form.is_valid():

            allocation = form.save(commit=False)

            item = allocation.item

            # Prevent over-allocation
            if allocation.quantity > item.quantity:

                return render(
                    request,
                    'allocations/create_allocation.html',
                    {
                        'form': form,
                        'error': 'Not enough stock available'
                    }
                )

            # Reduce stock
            item.quantity -= allocation.quantity

            item.save()

            allocation.allocated_by = request.user

            allocation.save()

            # Create stock movement
            StockMovement.objects.create(
                item=item,
                movement_type='OUT',
                quantity=allocation.quantity,
                performed_by=request.user
            )

            return redirect('allocation_list')

    else:
        form = AllocationForm()

    return render(request,
                  'allocations/create_allocation.html',
                  {'form': form})