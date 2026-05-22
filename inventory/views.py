from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.db import models
from .models import Item, Category


from .models import Item, StockMovement
from .forms import ItemForm

from users.permissions import (
    is_storesman,
    is_accounts,
    is_principal,
)




@login_required
def inventory_list(request):

    items = Item.objects.all()

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

            return redirect('inventory_list')

    else:
        form = ItemForm()

    return render(request, 'inventory/add_stock.html', {
        'form': form
    })


@login_required
@user_passes_test(is_storesman)
def edit_stock(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    old_quantity = item.quantity

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

            return redirect('inventory_list')

    else:
        form = ItemForm(instance=item)

    return render(request, 'inventory/edit_stock.html', {
        'form': form
    })


@login_required
@user_passes_test(is_storesman)
def delete_stock(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':

        item.delete()

        return redirect('inventory_list')

    return render(request, 'inventory/delete_stock.html', {
        'item': item
    })


# @login_required
# @user_passes_test(is_accounts)
# def accounts_dashboard(request):

#     return render(request, 'inventory/accounts_dashboard.html')


# @login_required
# @user_passes_test(is_principal)
# def principal_dashboard(request):

#     items = Item.objects.all()

#     return render(request, 'inventory/principal_dashboard.html', {
#         'items': items
#     })






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