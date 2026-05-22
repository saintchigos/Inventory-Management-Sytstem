from django.http import HttpResponse
from django.contrib.auth.decorators import (
    login_required
)

import openpyxl

from inventory.models import Item


@login_required
def export_inventory_excel(request):

    # Create workbook
    workbook = openpyxl.Workbook()

    worksheet = workbook.active

    worksheet.title = 'Inventory Report'

    # Headers
    headers = [
        'Item Name',
        'Category',
        'Quantity',
        'Minimum Stock',
        'Location',
    ]

    worksheet.append(headers)

    # Inventory data
    items = Item.objects.all()

    for item in items:

        worksheet.append([
            item.name,
            str(item.category),
            item.quantity,
            item.minimum_stock,
            str(item.location),
        ])

    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename=inventory_report.xlsx'
    )

    workbook.save(response)

    return response