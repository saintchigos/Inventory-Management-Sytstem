from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)
from django.utils import timezone

from procurement.models import ProcurementRequest
from procurement.forms import PaymentProofForm

from users.permissions import is_accounts


@login_required
@user_passes_test(is_accounts)
def accounts_dashboard(request):

    pending_requests = ProcurementRequest.objects.filter(
        status='PENDING'
    ).order_by('-created_at')

    waiting_payment_requests = ProcurementRequest.objects.filter(
        status='WAITING_PAYMENT'
    ).order_by('-updated_at')

    payment_received_requests = ProcurementRequest.objects.filter(
        status='PAYMENT_RECEIVED'
    ).order_by('-payment_received_at')[:10]

    rejected_requests = ProcurementRequest.objects.filter(
        status='REJECTED'
    ).order_by('-created_at')

    return render(request, 'accounts/dashboard.html', {
        'pending_requests': pending_requests,
        'waiting_payment_requests': waiting_payment_requests,
        'payment_received_requests': payment_received_requests,
        'rejected_requests': rejected_requests,
    })


@login_required
@user_passes_test(is_accounts)
def request_detail(request, request_id):

    procurement = get_object_or_404(
        ProcurementRequest,
        id=request_id
    )

    quotations = procurement.quotations.all()

    payment_form = PaymentProofForm()

    return render(request, 'accounts/request_detail.html', {
        'procurement': procurement,
        'quotations': quotations,
        'payment_form': payment_form,
    })


@login_required
@user_passes_test(is_accounts)
def payments(request):
    """
    Dedicated Accounts view of the payment stage of the procurement
    pipeline: what's still waiting on payment, and what's already been
    paid and evidenced with proof of payment.
    """

    waiting_payment_requests = ProcurementRequest.objects.filter(
        status='WAITING_PAYMENT'
    ).select_related('requested_by', 'accounts_approved_by', 'selected_quotation').order_by('-updated_at')

    paid_requests = ProcurementRequest.objects.filter(
        status__in=['PAYMENT_RECEIVED', 'DELIVERED']
    ).select_related('requested_by', 'payment_confirmed_by').order_by('-payment_received_at')

    payment_form = PaymentProofForm()

    return render(request, 'accounts/payments.html', {
        'waiting_payment_requests': waiting_payment_requests,
        'paid_requests': paid_requests,
        'payment_form': payment_form,
    })


@login_required
@user_passes_test(is_accounts)
def upload_payment_proof(request, request_id):

    procurement = get_object_or_404(
        ProcurementRequest,
        id=request_id,
        status='WAITING_PAYMENT'
    )

    if request.method == 'POST':

        form = PaymentProofForm(
            request.POST,
            request.FILES,
            instance=procurement
        )

        if form.is_valid():

            procurement = form.save(commit=False)

            procurement.status = 'PAYMENT_RECEIVED'
            procurement.payment_confirmed_by = request.user
            procurement.payment_received_at = timezone.now()

            procurement.save()

    next_url = request.POST.get('next')

    if next_url == 'request_detail':
        return redirect('request_detail', request_id=request_id)

    return redirect('accounts_payments')