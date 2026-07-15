from django.db import migrations


def migrate_approved_requests(apps, schema_editor):
    """
    Under the old flow, 'APPROVED' meant accounts had both approved the
    request AND already uploaded proof of payment in the same step, so
    those requests are equivalent to the new 'PAYMENT_RECEIVED' stage.
    """
    ProcurementRequest = apps.get_model('procurement', 'ProcurementRequest')

    for procurement in ProcurementRequest.objects.filter(status='APPROVED'):
        procurement.status = 'PAYMENT_RECEIVED'
        if procurement.payment_proof:
            procurement.payment_confirmed_by = procurement.accounts_approved_by
            procurement.payment_received_at = procurement.updated_at
        procurement.save()


def reverse_migration(apps, schema_editor):
    ProcurementRequest = apps.get_model('procurement', 'ProcurementRequest')

    for procurement in ProcurementRequest.objects.filter(status='PAYMENT_RECEIVED'):
        procurement.status = 'APPROVED'
        procurement.save()


class Migration(migrations.Migration):

    dependencies = [
        ('procurement', '0007_procurementrequest_payment_tracking'),
    ]

    operations = [
        migrations.RunPython(migrate_approved_requests, reverse_migration),
    ]
