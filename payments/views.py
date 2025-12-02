import uuid
import json
import requests
from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from courses.models import Course, CourseProgress
from .models import Payment

def initiate_payment(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = request.user

    # 1. Generate Transaction ID
    tran_id = uuid.uuid4().hex[:16]
    amount = str(course.price) 

    Payment.objects.create(
        user=user, 
        course=course, 
        tran_id=tran_id, 
        amount=amount,
        status="PENDING"
    )

    api_url = f"{settings.PIPRAPAY_BASE_URL}/create-charge"
    
    # PipraPay seems to strip query params, but we keep this just in case
    success_url = request.build_absolute_uri(f'/payments/success/?tran_id={tran_id}')
    cancel_url = request.build_absolute_uri('/payments/cancel/')
    webhook_url = request.build_absolute_uri('/payments/webhook/')

    payload = {
        "full_name": user.get_full_name() or user.username,
        "email_mobile": user.email,
        "amount": amount,
        "currency": "BDT",
        "redirect_url": success_url, 
        "cancel_url": cancel_url,
        "webhook_url": webhook_url,
        "return_type": "GET",
        "metadata": {
            "invoiceid": tran_id,
            "course_id": course.id
        }
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Mh-Piprapay-Api-Key": settings.PIPRAPAY_API_KEY
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200 and data.get('pp_url'):
            return redirect(data['pp_url'])
        else:
            print(f"PipraPay Init Error: {data}")
            return render(request, 'payments/fail.html', {'error': 'Failed to initiate payment'})

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
        return render(request, 'payments/fail.html')


@csrf_exempt
def payment_success(request):
    """
    Handle return from PipraPay.
    URL looks like: /payments/success/?pp_id=1352978145
    """
    # --- FIX 1: Get 'pp_id' from URL instead of 'payment_id' ---
    payment_id = request.GET.get('pp_id') 
    
    # Fallback: check 'payment_id' just in case they change it back
    if not payment_id:
        payment_id = request.GET.get('payment_id')

    # Debugging print to see what we received
    print(f"DEBUG: Received payment_id: {payment_id}")
    
    if not payment_id:
         print("DEBUG: No payment ID found in URL parameters")
         return render(request, 'payments/fail.html', {'error': 'No payment ID returned'})

    # 1. Verify Payment with API
    is_verified, verified_data = verify_piprapay_payment(payment_id)

    if is_verified:
        # 2. Extract Transaction ID from the VERIFICATION RESPONSE metadata
        # Since PipraPay stripped 'tran_id' from the URL, we rely on metadata here.
        metadata = verified_data.get('metadata', {})
        tran_id = metadata.get('invoiceid')
        
        print(f"DEBUG: Verified. Tran ID from metadata: {tran_id}")

        if not tran_id:
             print("DEBUG: Transaction ID missing in verification metadata")
             return render(request, 'payments/fail.html', {'error': 'Transaction ID missing in gateway response'})

        try:
            payment = Payment.objects.get(tran_id=tran_id)
            
            if payment.status != "VALID":
                payment.val_id = payment_id
                payment.status = "VALID"
                payment.save()

                CourseProgress.objects.get_or_create(
                    user=payment.user,
                    course=payment.course,
                    defaults={'enrolled': True}
                )

            return render(request, 'payments/success.html', {'payment': payment})

        except Payment.DoesNotExist:
            print(f"DEBUG: Payment record not found for tran_id: {tran_id}")
            return render(request, 'payments/fail.html', {'error': 'Order not found in database'})

    print("DEBUG: Verification failed")
    return render(request, 'payments/fail.html', {'error': 'Payment verification failed'})


def verify_piprapay_payment(payment_id):
    verify_url = f"{settings.PIPRAPAY_BASE_URL}/verify-payments"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Mh-Piprapay-Api-Key": settings.PIPRAPAY_API_KEY
    }
    
    # We send the ID we received ('pp_id' value) as 'payment_id' in payload
    payload = {"pp_id": payment_id}
    
    print("DEBUG: Verifying payment with payload:", payload) 

    try:
        response = requests.post(verify_url, json=payload, headers=headers)
        data = response.json()
        
        # Debug the verification response
        print(f"DEBUG: Verify Response: {data}")

        if data.get('status') == 'completed' or data.get('status') == 'success':
            return True, data
            
    except Exception as e:
        print(f"Verification Network Error: {e}")
    
    return False, {}


# @csrf_exempt
# def piprapay_webhook(request):
#     if request.method != "POST":
#         return JsonResponse({"status": False, "message": "Method not allowed"}, status=405)

#     received_key = request.headers.get('Mh-Piprapay-Api-Key') or \
#                    request.headers.get('mh-piprapay-api-key')

#     if received_key != settings.PIPRAPAY_API_KEY:
#         return JsonResponse({"status": False, "message": "Unauthorized request."}, status=401)

#     try:
#         data = json.loads(request.body)
        
#         pp_id = data.get('pp_id')
#         status = data.get('status')
#         metadata = data.get('metadata', {})
#         tran_id = metadata.get('invoiceid')

#         if status == 'completed' and tran_id:
#             try:
#                 payment = Payment.objects.get(tran_id=tran_id)
#                 if payment.status != "VALID":
#                     payment.status = "VALID"
#                     payment.val_id = pp_id
#                     payment.save()
                    
#                     CourseProgress.objects.get_or_create(
#                         user=payment.user,
#                         course=payment.course,
#                         defaults={'enrolled': True}
#                     )
#             except Payment.DoesNotExist:
#                 pass 

#         return JsonResponse({'status': True, 'message': 'Webhook received'})

#     except json.JSONDecodeError:
#         return JsonResponse({"status": False, "message": "Invalid JSON"}, status=400)





@csrf_exempt
def payment_fail(request):
    return render(request, 'payments/fail.html')

@csrf_exempt
def payment_cancel(request):
    return render(request, 'payments/cancel.html')


