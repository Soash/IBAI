import uuid
from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_lib import SSLCOMMERZ
from courses.models import Course, CourseProgress
from .models import Payment

def initiate_payment(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = request.user

    tran_id = uuid.uuid4().hex[:16]
    amount = course.price

    settings_data = settings.SSLCOMMERZ
    sslcz = SSLCOMMERZ(settings_data)

    post_body = {
        'total_amount': amount,
        'currency': "BDT",
        'tran_id': tran_id,
        'success_url': request.build_absolute_uri('/payments/success/'),
        'fail_url': request.build_absolute_uri('/payments/fail/'),
        'cancel_url': request.build_absolute_uri('/payments/cancel/'),
        'emi_option': 0,
        'cus_name': user.get_full_name() or user.username,
        'cus_email': user.email,
        'cus_phone': "01700000000",
        'cus_add1': "Customer Address",
        'cus_city': "Dhaka",
        'cus_country': "Bangladesh",
        'shipping_method': "NO",
        'product_name': course.title,
        'product_category': "Course",
        'product_profile': "general",
    }

    # Create local payment record
    Payment.objects.create(user=user, course=course, tran_id=tran_id, amount=amount)

    response = sslcz.createSession(post_body)
    
    # Redirect to SSLCOMMERZ payment page
    return redirect(response['GatewayPageURL'])


@csrf_exempt
def payment_success(request):
    val_id = request.POST.get('val_id')
    tran_id = request.POST.get('tran_id')
    amount = request.POST.get('amount')
    status = request.POST.get('status')

    if status == "VALID":
        payment = Payment.objects.get(tran_id=tran_id)
        payment.val_id = val_id
        payment.status = status
        payment.save()

        course_progress, created = CourseProgress.objects.get_or_create(
            user=payment.user,
            course=payment.course,
            enrolled=True,
        )
    
        return render(request, 'payments/success.html', {'payment': payment})

    return render(request, 'payments/fail.html')


@csrf_exempt
def payment_fail(request):
    return render(request, 'payments/fail.html')


@csrf_exempt
def payment_cancel(request):
    return render(request, 'payments/cancel.html')
