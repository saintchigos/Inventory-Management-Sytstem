from django.http import HttpResponse
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

import openpyxl

from inventory.models import Item
from allocations.models import Allocation

from users.permissions import is_principal


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


@login_required
@user_passes_test(is_principal)
def export_allocations_excel(request):

    workbook = openpyxl.Workbook()

    worksheet = workbook.active

    worksheet.title = 'Allocations Report'

    headers = [
        'Item Name',
        'Department',
        'Quantity',
        'Receiver',
        'Allocated By',
        'Date Allocated',
        'Notes',
    ]

    worksheet.append(headers)

    allocations = Allocation.objects.select_related(
        'item', 'department', 'allocated_by'
    ).order_by('-date_allocated')

    for allocation in allocations:

        worksheet.append([
            str(allocation.item.name) if allocation.item else '',
            str(allocation.department),
            allocation.quantity,
            allocation.receiver_name,
            str(allocation.allocated_by) if allocation.allocated_by else '',
            allocation.date_allocated.strftime('%Y-%m-%d %H:%M') if allocation.date_allocated else '',
            allocation.notes or '',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename=allocations_report.xlsx'
    )

    workbook.save(response)

    return response