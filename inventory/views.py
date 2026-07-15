from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.db import models
from .models import Item, Category


from .models import Item, StockMovement, InventoryAuditLog
from .forms import ItemForm

from users.permissions import (
    is_storesman,
    is_accounts,
    is_principal,
)



# View for listing inventory items
def is_storesman_or_procurement(user):
    return user.role in ['storesman', 'procurement']


@login_required
@user_passes_test(is_storesman_or_procurement)
def inventory_list(request):

    # Get all items and order by name
    items = Item.objects.all().order_by('name')

    # Search
    search_query = request.GET.get('search')

    if search_query:

        items = items.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Low stock filter
    low_stock = request.GET.get('low_stock')

    if low_stock:

        items = items.filter(
            quantity__lte=models.F('minimum_stock')
        )

    # Category filter
    category = request.GET.get('category')

    if category:

        items = items.filter(
            category__id=category
        )

    categories = Category.objects.all()

    return render(request,
                  'inventory/inventory_list.html',
                  {
                      'items': items,
                      'categories': categories,
                  })

# View for adding new stock
@login_required
@user_passes_test(is_storesman)
def add_stock(request):

    if request.method == 'POST':

        form = ItemForm(request.POST)

        if form.is_valid():

            item = form.save()

            # Create stock movement
            StockMovement.objects.create(
                item=item,
                movement_type='IN',
                quantity=item.quantity,
                performed_by=request.user
            )

            # Audit log
            InventoryAuditLog.objects.create(
                item_name=item.name,
                action='CREATED',
                details=f"Item created with quantity {item.quantity}.",
                performed_by=request.user
            )

            return redirect('inventory_list')

    else:
        form = ItemForm()

    return render(request, 'inventory/add_stock.html', {
        'form': form
    })


# View for editing stock
@login_required
@user_passes_test(is_storesman)
def edit_stock(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    old_quantity = item.quantity
    old_name = item.name
    old_category = item.category
    old_location = item.location
    old_minimum_stock = item.minimum_stock

    if request.method == 'POST':

        form = ItemForm(request.POST, instance=item)

        if form.is_valid():

            updated_item = form.save()

            quantity_difference = updated_item.quantity - old_quantity

            if quantity_difference != 0:

                movement_type = 'IN'

                if quantity_difference < 0:
                    movement_type = 'OUT'

                StockMovement.objects.create(
                    item=updated_item,
                    movement_type=movement_type,
                    quantity=abs(quantity_difference),
                    performed_by=request.user
                )

            # Build a readable summary of what changed
            changes = []

            if old_name != updated_item.name:
                changes.append(f"Name: '{old_name}' -> '{updated_item.name}'")

            if old_category != updated_item.category:
                changes.append(f"Category: '{old_category}' -> '{updated_item.category}'")

            if old_location != updated_item.location:
                changes.append(f"Location: '{old_location}' -> '{updated_item.location}'")

            if old_minimum_stock != updated_item.minimum_stock:
                changes.append(f"Minimum stock: {old_minimum_stock} -> {updated_item.minimum_stock}")

            if quantity_difference != 0:
                changes.append(f"Quantity: {old_quantity} -> {updated_item.quantity}")

            if changes:

                InventoryAuditLog.objects.create(
                    item_name=updated_item.name,
                    action='EDITED',
                    details="; ".join(changes),
                    performed_by=request.user
                )

            return redirect('inventory_list')

    else:
        form = ItemForm(instance=item)

    return render(request, 'inventory/edit_stock.html', {
        'form': form
    })


# View for deleting stock
@login_required
@user_passes_test(is_storesman)
def delete_stock(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':

        item_name = item.name
        item_quantity = item.quantity

        item.delete()

        # Audit log (snapshot taken before deletion, since the item is now gone)
        InventoryAuditLog.objects.create(
            item_name=item_name,
            action='DELETED',
            details=f"Item deleted while it had {item_quantity} units in stock.",
            performed_by=request.user
        )

        return redirect('inventory_list')

    return render(request, 'inventory/delete_stock.html', {
        'item': item
    })


import json

from django.db.models import Sum
from django.db import models

from users.permissions import is_storesman


@login_required
@user_passes_test(is_storesman)
def storesman_dashboard(request):

    items = Item.objects.all()

    total_items = items.count()

    total_quantity = items.aggregate(
        Sum('quantity')
    )['quantity__sum']

    low_stock_items = items.filter(
        quantity__lte=models.F('minimum_stock')
    )

    category_data = (
        items.values('category__name')
        .annotate(total=Sum('quantity'))
    )

    category_labels = [
        item['category__name']
        for item in category_data
    ]

    category_totals = [
        item['total']
        for item in category_data
    ]

    context = {

        'items': items,

        'total_items': total_items,

        'total_quantity': total_quantity,

        'low_stock_items': low_stock_items,

        'category_labels_json': json.dumps(category_labels),

        'category_totals_json': json.dumps(category_totals),
    }

    return render(
        request,
        'inventory/storesman_dashboard.html',
        context
    )


def is_storesman_or_principal(user):
    return user.role in ['storesman', 'principal']


@login_required
@user_passes_test(is_storesman_or_principal)
def stock_movements(request):

    movements = StockMovement.objects.all().order_by('-date')

    return render(request, 'inventory/stock_movements.html', {
        'movements': movements
    })


@login_required
@user_passes_test(is_principal)
def inventory_audit(request):

    logs = InventoryAuditLog.objects.all().order_by('-timestamp')

    return render(request, 'inventory/inventory_audit.html', {
        'logs': logs
    })