from django.shortcuts import render
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

from procurement.models import ProcurementRequest

from users.permissions import is_accounts


@login_required
@user_passes_test(is_accounts)
def accounts_dashboard(request):

    pending_requests = ProcurementRequest.objects.filter(
        status='PENDING'
    )

    approved_requests = ProcurementRequest.objects.filter(
        status='APPROVED'
    )

    return render(request, 'accounts/dashboard.html', {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
    })