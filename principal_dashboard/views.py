from django.shortcuts import render

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

from django.db.models import Sum
from django.db import models

from inventory.models import Item

from users.permissions import is_principal


@login_required
@user_passes_test(is_principal)
def principal_dashboard(request):

    items = Item.objects.all()

    total_items = items.count()

    total_quantity = items.aggregate(
        Sum('quantity')
    )['quantity__sum']

    low_stock_items = items.filter(
        quantity__lte=models.F('minimum_stock')
    )

    # Chart Data
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

    return render(request,
                  'principal/dashboard.html',
                  {
                      'items': items,
                      'total_items': total_items,
                      'total_quantity': total_quantity,
                      'low_stock_items': low_stock_items,

                      'category_labels': category_labels,
                      'category_totals': category_totals,
                  })