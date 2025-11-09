from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from courses.models import CourseProgress


@login_required
def student_dashboard(request):
    user = request.user

    # Get all enrolled courses
    enrolled_courses = (
        CourseProgress.objects.filter(user=user, enrolled=True)
        .select_related('course')
        .order_by('-enrolled_at')
    )

    # Separate completed and ongoing courses
    completed_courses = enrolled_courses.filter(completed=True)
    ongoing_courses = enrolled_courses.filter(completed=False)
    
    context = {
        "completed_courses": completed_courses,
        "ongoing_courses": ongoing_courses,
    }

    return render(request, "dashboard/student-dashboard.html", context)

@login_required
def student_profile(request):
    return render(request, 'dashboard/student-profile.html')

@login_required
def student_courses(request):
    user = request.user

    # Get all enrolled courses
    enrolled_courses = (
        CourseProgress.objects.filter(user=user, enrolled=True)
        .select_related('course')
        .order_by('-enrolled_at')
    )

    # Separate completed and ongoing courses
    completed_courses = enrolled_courses.filter(completed=True)
    ongoing_courses = enrolled_courses.filter(completed=False)
    
    context = {
        "completed_courses": completed_courses,
        "ongoing_courses": ongoing_courses,
    }
    return render(request, "dashboard/student-courses.html", context)










@login_required
def student_assignments(request):
    return render(request, 'dashboard/student-assignments.html')

@login_required
def student_enrolled_courses(request):
    return render(request, 'dashboard/student-enrolled-courses.html')


@login_required
def student_message(request):
    return render(request, 'dashboard/student-message.html')

@login_required
def student_quiz(request):
    return render(request, 'dashboard/student-quiz.html')

@login_required
def student_reviews(request):
    return render(request, 'dashboard/student-reviews.html')

@login_required
def student_settings(request):
    return render(request, 'dashboard/student-settings.html')

@login_required
def student_wishlist(request):
    return render(request, 'dashboard/student-wishlist.html')

