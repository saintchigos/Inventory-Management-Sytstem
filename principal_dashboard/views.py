import json

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)
from django.db.models import Sum, Q
from django.db import models

from inventory.models import Item, StockMovement, InventoryAuditLog, Category
from procurement.models import ProcurementRequest
from allocations.models import Allocation, Department

from users.models import User
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

    # Procurement summary counts
    requests = ProcurementRequest.objects.all()

    draft_count = requests.filter(status='DRAFT').count()
    pending_count = requests.filter(status='PENDING').count()
    waiting_payment_count = requests.filter(status='WAITING_PAYMENT').count()
    payment_received_count = requests.filter(status='PAYMENT_RECEIVED').count()
    rejected_count = requests.filter(status='REJECTED').count()
    delivered_count = requests.filter(status='DELIVERED').count()

    recent_requests = requests.order_by('-created_at')[:5]

    # Allocation summary
    allocations = Allocation.objects.all()

    total_allocations = allocations.count()

    total_allocated_quantity = allocations.aggregate(
        Sum('quantity')
    )['quantity__sum'] or 0

    # User counts
    total_users = User.objects.count()

    users_by_role = []

    for role_value, role_label in User.ROLE_CHOICES:
        count = User.objects.filter(role=role_value).count()
        users_by_role.append({
            'label': role_label,
            'count': count
        })

    # Combined system activity feed
    activity_category = request.GET.get('activity_category', '')

    activity = []

    for movement in StockMovement.objects.select_related('item', 'performed_by').order_by('-date')[:40]:
        activity.append({
            'timestamp': movement.date,
            'category': 'Stock Movement',
            'description': f"{movement.get_movement_type_display()} — {movement.item.name} ({movement.quantity})",
            'performed_by': movement.performed_by,
        })

    for log in InventoryAuditLog.objects.select_related('performed_by').order_by('-timestamp')[:40]:
        activity.append({
            'timestamp': log.timestamp,
            'category': 'Inventory Change',
            'description': f"{log.get_action_display()} — {log.item_name}",
            'performed_by': log.performed_by,
        })

    for req in ProcurementRequest.objects.select_related('requested_by').order_by('-created_at')[:40]:
        activity.append({
            'timestamp': req.created_at,
            'category': 'Procurement',
            'description': f"Request created — {req.display_name()} ({req.get_status_display()})",
            'performed_by': req.requested_by,
        })

    # --- Inventory Overview: filters + "view more" pagination ---
    inv_items = items.select_related('category').order_by('name')

    inv_search = request.GET.get('inv_search', '').strip()
    if inv_search:
        inv_items = inv_items.filter(
            Q(name__icontains=inv_search) | Q(location__icontains=inv_search)
        )

    inv_category = request.GET.get('inv_category', '')
    if inv_category:
        inv_items = inv_items.filter(category__id=inv_category)

    inv_status = request.GET.get('inv_status', '')
    if inv_status == 'low':
        inv_items = inv_items.filter(quantity__lte=models.F('minimum_stock'))
    elif inv_status == 'ok':
        inv_items = inv_items.filter(quantity__gt=models.F('minimum_stock'))

    inventory_paginator = Paginator(inv_items, 10)
    inv_page_number = request.GET.get('inv_page', 1)
    inventory_page = inventory_paginator.get_page(inv_page_number)

    categories = Category.objects.all()

    # Accounts actions (approvals to waiting-payment, payment confirmations, rejections)
    accounts_actions = ProcurementRequest.objects.filter(
        status__in=['WAITING_PAYMENT', 'PAYMENT_RECEIVED', 'DELIVERED', 'REJECTED']
    ).select_related('accounts_approved_by', 'payment_confirmed_by').order_by('-updated_at')[:40]

    for req in accounts_actions:
        if req.status == 'REJECTED':
            activity.append({
                'timestamp': req.updated_at,
                'category': 'Accounts',
                'description': f"Rejected — {req.display_name()} (Qty {req.requested_quantity})",
                'performed_by': req.accounts_approved_by,
            })
        else:
            # Every request that reached this far was first approved into Waiting for Payment
            if req.accounts_approved_by:
                activity.append({
                    'timestamp': req.updated_at,
                    'category': 'Accounts',
                    'description': f"Approved — {req.display_name()} moved to Waiting for Payment (Qty {req.requested_quantity})",
                    'performed_by': req.accounts_approved_by,
                })

            if req.payment_received_at:
                activity.append({
                    'timestamp': req.payment_received_at,
                    'category': 'Accounts',
                    'description': f"Payment Received — proof uploaded for {req.display_name()} (Qty {req.requested_quantity})",
                    'performed_by': req.payment_confirmed_by,
                })

    for allocation in Allocation.objects.select_related('item', 'department', 'allocated_by').order_by('-date_allocated')[:40]:
        activity.append({
            'timestamp': allocation.date_allocated,
            'category': 'Allocation',
            'description': f"{allocation.item.name} ({allocation.quantity}) → {allocation.department.name}, for {allocation.receiver_name}",
            'performed_by': allocation.allocated_by,
        })

    activity.sort(key=lambda entry: entry['timestamp'], reverse=True)

    activity_categories = ['Stock Movement', 'Inventory Change', 'Procurement', 'Accounts', 'Allocation']

    if activity_category:
        activity = [entry for entry in activity if entry['category'] == activity_category]

    # Cap the overall pool the feed pulls from, then page it for "view more"
    activity = activity[:100]

    activity_paginator = Paginator(activity, 10)
    activity_page_number = request.GET.get('activity_page', 1)
    activity_page = activity_paginator.get_page(activity_page_number)

    return render(request,
                  'principal/dashboard.html',
                  {
                      'items': items,
                      'total_items': total_items,
                      'total_quantity': total_quantity,
                      'low_stock_items': low_stock_items,

                      'category_labels_json': json.dumps(category_labels),
                      'category_totals_json': json.dumps(category_totals),

                      'draft_count': draft_count,
                      'pending_count': pending_count,
                      'waiting_payment_count': waiting_payment_count,
                      'payment_received_count': payment_received_count,
                      'rejected_count': rejected_count,
                      'delivered_count': delivered_count,

                      'recent_requests': recent_requests,

                      'total_allocations': total_allocations,
                      'total_allocated_quantity': total_allocated_quantity,

                      'total_users': total_users,
                      'users_by_role': users_by_role,

                      # Inventory Overview: filters + pagination
                      'inventory_page': inventory_page,
                      'categories': categories,
                      'inv_search': inv_search,
                      'inv_category': inv_category,
                      'inv_status': inv_status,

                      # System Activity Feed: filter + pagination
                      'activity_page': activity_page,
                      'activity_categories': activity_categories,
                      'activity_category': activity_category,
                  })


@login_required
@user_passes_test(is_principal)
def procurement_audit(request):

    requests = ProcurementRequest.objects.all().order_by('-created_at')

    status_filter = request.GET.get('status')

    if status_filter:
        requests = requests.filter(status=status_filter)

    actioned_by_filter = request.GET.get('actioned_by')

    if actioned_by_filter:
        requests = requests.filter(accounts_approved_by__id=actioned_by_filter)

    accounts_users = User.objects.filter(role='accounts')

    return render(request, 'principal/procurement_audit.html', {
        'requests': requests,
        'status_filter': status_filter,
        'accounts_users': accounts_users,
        'actioned_by_filter': actioned_by_filter,
    })


@login_required
@user_passes_test(is_principal)
def accounts_activity(request):
    """
    Gives the principal a dedicated view of what the Accounts team has
    been doing across the full payment pipeline: requests approved into
    Waiting for Payment, payments confirmed with proof, and rejections —
    plus a per-person summary so it's obvious who has actioned what.
    """

    actioned_requests = ProcurementRequest.objects.filter(
        status__in=['WAITING_PAYMENT', 'PAYMENT_RECEIVED', 'DELIVERED', 'REJECTED']
    ).select_related(
        'accounts_approved_by', 'payment_confirmed_by', 'requested_by'
    ).order_by('-updated_at')

    accounts_users = User.objects.filter(role='accounts')

    summary = []

    for accounts_user in accounts_users:
        approved_requests = ProcurementRequest.objects.filter(
            accounts_approved_by=accounts_user
        ).exclude(status='PENDING').exclude(status='DRAFT')

        confirmed_payments = ProcurementRequest.objects.filter(
            payment_confirmed_by=accounts_user
        )

        summary.append({
            'user': accounts_user,
            'approved_count': approved_requests.exclude(status='REJECTED').count(),
            'rejected_count': approved_requests.filter(status='REJECTED').count(),
            'payments_confirmed_count': confirmed_payments.count(),
            'total_count': approved_requests.count(),
        })

    return render(request, 'principal/accounts_activity.html', {
        'actioned_requests': actioned_requests,
        'summary': summary,
    })


@login_required
@user_passes_test(is_principal)
def user_directory(request):
    """
    Read-only, full-system view of every account in the system, across
    every role, so the principal has complete oversight of who has
    access and to what.
    """

    users = User.objects.all().order_by('role', 'username')

    role_filter = request.GET.get('role')

    if role_filter:
        users = users.filter(role=role_filter)

    return render(request, 'principal/user_directory.html', {
        'users': users,
        'role_choices': User.ROLE_CHOICES,
        'role_filter': role_filter,
    })


@login_required
@user_passes_test(is_principal)
def allocation_audit(request):
    """
    Full oversight of every stock allocation made to every department,
    plus a per-department summary so the principal can see where
    stock is actually going.
    """

    allocations = Allocation.objects.select_related(
        'item', 'department', 'allocated_by'
    ).order_by('-date_allocated')

    department_filter = request.GET.get('department')

    if department_filter:
        allocations = allocations.filter(department__id=department_filter)

    departments = Department.objects.all()

    summary = []

    for department in departments:
        dept_allocations = Allocation.objects.filter(department=department)

        summary.append({
            'department': department,
            'total_quantity': dept_allocations.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'allocation_count': dept_allocations.count(),
        })

    return render(request, 'principal/allocation_audit.html', {
        'allocations': allocations,
        'departments': departments,
        'department_filter': department_filter,
        'summary': summary,
    })


@login_required
@user_passes_test(is_principal)
def request_audit_detail(request, request_id):

    procurement = get_object_or_404(ProcurementRequest, id=request_id)

    quotations = procurement.quotations.all()

    return render(request, 'principal/request_detail.html', {
        'procurement': procurement,
        'quotations': quotations,
    })