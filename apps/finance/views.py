import json
import hmac
import hashlib
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from apps.finance.models import StudentFeeStatus, PaymentTransaction
from apps.academics.models import StudentProfile, TermSession

@csrf_exempt
def paystack_webhook(request):
    """
    Receives and validates Paystack IPN webhooks.
    Automatically clears fees and unlocks result viewing.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    signature = request.headers.get('x-paystack-signature')
    secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', '').encode('utf-8')

    if not secret_key:
        return HttpResponse(status=500)

    computed = hmac.new(secret_key, request.body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(computed, signature or ''):
        return HttpResponse(status=400)

    payload = json.loads(request.body.decode('utf-8'))
    event = payload.get('event')

    if event == 'charge.success':
        data = payload.get('data', {})
        reference = data.get('reference')
        amount_kobo = data.get('amount', 0)
        amount_naira = Decimal(amount_kobo) / 100
        metadata = data.get('metadata', {})
        student_id = metadata.get('student_id')
        term_session_id = metadata.get('term_session_id')

        if student_id and term_session_id:
            try:
                student = StudentProfile.objects.get(id=student_id)
                term = TermSession.objects.get(id=term_session_id)
                fee_record = StudentFeeStatus.objects.get(student=student, term_session=term)
                
                fee_record.total_paid += amount_naira
                fee_record.save()

                PaymentTransaction.objects.create(
                    student=student,
                    term_session=term,
                    reference=reference,
                    amount=amount_naira,
                    channel='PAYSTACK',
                    is_successful=True
                )
            except Exception:
                return HttpResponse(status=500)

    return HttpResponse(status=200)

def verify_payment_callback(request):
    """
    Handles browser return after Paystack popup payment.
    """
    reference = request.GET.get('reference')
    messages.success(request, f"Payment received (Ref: {reference}). Verifying clearance...")
    return redirect('portal:dashboard')
