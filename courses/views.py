import uuid
from django.contrib import messages
from django.db import models
import urllib.parse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    Course, ExamAttempt, Lesson, Video, VideoProgress,
    Exam, ExamProgress,
    CourseProgress, Comment
)
import urllib.parse
from django.utils import timezone


def course_list(request):
    courses = Course.objects.filter(published=True)

    total_courses = courses.count()
    context = {
        'courses': courses,
        'total_courses': total_courses,
    }
    return render(request, 'courses/course-list.html', context)

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, published=True)
    # print(f"Course: {course.title} (slug: {course.slug})")

    lessons = course.lessons.prefetch_related('video', 'exam').all()
    # print(f"Total lessons: {lessons.count()}")

    for lesson in lessons:
        videos = list(lesson.video.all())
        exams = list(lesson.exam.all())
        lesson.total_duration = sum(v.video_length_min or 0 for v in videos)
        
    total_videos = Video.objects.filter(lesson__course=course).count()
    total_duration = Video.objects.filter(lesson__course=course).aggregate(total=models.Sum('video_length_min'))['total'] or 0
    total_duration_str = (
        f"{total_duration} min" if total_duration < 60
        else f"{total_duration // 60}hr {total_duration % 60}min" if total_duration % 60 else f"{total_duration // 60}hr"
    )
    total_enrollments = CourseProgress.objects.filter(course=course, enrolled=True).count()
    comments = Comment.objects.filter(course=course).order_by('-created_at')
    total_comments = comments.count()

    parsed_url = urllib.parse.urlparse(course.intro_video_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    video_id = query_params.get("v", [""])[0]
    intro_video_thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    is_enrolled = request.user.is_authenticated and CourseProgress.objects.filter(
        user=request.user, course=course, enrolled=True
    ).exists()

    context = {
        'course': course,
        'lessons': lessons,
        'total_videos': total_videos,
        'total_duration': total_duration_str,
        'intro_video_thumbnail': intro_video_thumbnail,
        'is_enrolled': is_enrolled,
        'total_enrollments': total_enrollments,
        'comments': comments,
        'total_comments': total_comments,
    }

    print("Context prepared, rendering template...")
    return render(request, 'courses/course-details.html', context)

@login_required
def add_comment(request, slug):
    """
    Handles posting a comment for a course.
    """
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(course=course, user=request.user, content=content)
            messages.success(request, "Your comment has been posted.")
        else:
            messages.warning(request, "Comment cannot be empty.")
    else:
        messages.warning(request, "Invalid request method.")

    return redirect('course_detail', slug=slug)

@login_required
def course_item(request, course_slug, lesson_slug, item_order):

    course = get_object_or_404(Course, slug=course_slug, published=True)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    
    is_enrolled = CourseProgress.objects.filter(
        user=request.user, course=course, enrolled=True
    ).exists()
    if not is_enrolled:
        messages.warning(request, "You must be enrolled in this course to access its content.")
        return redirect('course_detail', slug=course.slug)
    
    lessons = course.lessons.prefetch_related('video', 'exam').all()
    videos = list(lesson.video.all())
    exams = list(lesson.exam.all())
    
    video_progress = None
    exam_progress = None
    exam_attempt = None
    item = None

    if item_order in [v.order for v in videos]:
        item = next(v for v in videos if v.order == item_order)
        item = Video.objects.get(lesson=lesson, order=item_order)
        video_progress, _ = VideoProgress.objects.get_or_create(user=request.user, video=item)
    elif item_order in [e.order for e in exams]:
        item = next(e for e in exams if e.order == item_order)
        item = Exam.objects.get(lesson=lesson, order=item_order)
        exam_progress, _ = ExamProgress.objects.get_or_create(user=request.user, exam=item)
     
            
    if request.method == 'POST' and 'mark_done' in request.POST:
        video_progress.status = True
        video_progress.save()
        
    if request.method == 'POST' and 'submit_exam' in request.POST:
        total = item.questions.count()
        score = 0

        for question in item.questions.all():
            selected_option_id = request.POST.get(f'question_{question.id}')
            if selected_option_id:
                selected_option = question.options.get(id=selected_option_id)
                if selected_option.is_correct:
                    score += 1

        percentage = (score / total) * 100 if total > 0 else 0

        # Only set new_status to True if previous score was not already >= 80
        prev_score = exam_progress.score if exam_progress else None
        if prev_score is not None and prev_score >= 80:
            new_status = True
        else:
            new_status = True if percentage >= 80 else False

        # Get or create progress record
        exam_progress, created = ExamProgress.objects.get_or_create(
            user=request.user,
            exam=item,
            defaults={'score': percentage, 'status': new_status}
        )

        if not created:
            # Update progress only — e.g., new score or status
            exam_progress.score = percentage
            exam_progress.status = new_status
            exam_progress.save()

        # Always log a new exam attempt
        ExamAttempt.objects.create(user=request.user, exam=item, score=percentage)

        # Give user feedback
        if percentage >= 80:
            messages.success(request, f"🎉 Exam passed! You scored {percentage:.0f}%.")
        else:
            messages.warning(request, f"⚠️ Exam failed. You scored {percentage:.0f}%. Try again.")

    if item.item_type == 'exam':
        exam_attempt = ExamAttempt.objects.filter(user=request.user, exam=item).order_by('attempted_at')
     
    
    # Check if all videos and exams in the course are completed by the user
    all_videos = Video.objects.filter(lesson__course=course)
    all_exams = Exam.objects.filter(lesson__course=course)
    completed_videos = VideoProgress.objects.filter(user=request.user, video__in=all_videos, status=True).count()
    completed_exams = ExamProgress.objects.filter(user=request.user, exam__in=all_exams, status=True).count()
    progress = CourseProgress.objects.get(user=request.user, course=course)
    all_completed = (completed_videos == all_videos.count() and completed_exams == all_exams.count() or progress.completed)
    if all_completed:
        if not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.certificate_id = f"IBAI-{uuid.uuid4().hex[:12].upper()}"
            progress.save()
            
    certificate_id = progress.certificate_id if progress.completed else None
    
    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'current_lesson_slug': lesson.slug,
        'item': item,
        'video_progress': video_progress,
        'exam_progress': exam_progress,
        'exam_attempt': exam_attempt,
        'all_completed': all_completed,
        'certificate_id': certificate_id,
    }
    return render(request, 'courses/course-item.html', context)




from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import qrcode
from io import BytesIO

def reportlab_certificate(request, certificate_id):
    # Fetch course progress
    course_progress = CourseProgress.objects.get(certificate_id=certificate_id)

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{certificate_id}_certificate.pdf"'

    # Page setup
    p = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Colors & styling
    border_color = colors.HexColor("#4B9CD3")
    text_color = colors.HexColor("#333333")

    # Draw border
    border_margin = 40
    p.setStrokeColor(border_color)
    p.setLineWidth(5)
    p.rect(border_margin, border_margin, width - 2 * border_margin, height - 2 * border_margin)

    # Add logo (top-center)
    logo_path = "static/img/logo/logo.jpg"
    try:
        p.drawImage(logo_path, width / 2 - 60, height - 150, width=120, height=120, mask='auto')
    except Exception as e:
        print(f"Logo not found: {e}")

    # Title
    p.setFont("Times-Bold", 40)
    p.setFillColor(text_color)
    p.drawCentredString(width / 2, height - 200, "Certificate of Achievement")

    # Subtitle
    p.setFont("Times-Italic", 20)
    p.setFillColor(colors.gray)
    p.drawCentredString(width / 2, height - 230, "This is to certify that")

    # Recipient name
    p.setFont("Times-Bold", 30)
    p.setFillColor(text_color)
    p.drawCentredString(width / 2, height - 280, str(course_progress.user.first_name or course_progress.user.username))

    # Course info
    p.setFont("Times-Roman", 20)
    p.setFillColor(text_color)
    p.drawCentredString(width / 2, height - 320, "has successfully completed the course")

    p.setFont("Times-BoldItalic", 26)
    p.setFillColor(colors.HexColor("#0072C6"))
    p.drawCentredString(width / 2, height - 360, course_progress.course.title)

    # Completion date
    date_text = course_progress.completed_at.strftime("Date of Completion: %B %d, %Y")
    p.setFont("Times-Italic", 16)
    p.setFillColor(colors.gray)
    p.drawCentredString(width / 2, height - 410, date_text)

    # Signature area
    sign_path = "static/img/logo/ceo-signature.png"
    try:
        p.drawImage(sign_path, width - 250, 120, width=180, height=70, mask='auto')
    except Exception as e:
        print(f"Signature not found: {e}")

    p.setFont("Times-Roman", 16)
    p.setFillColor(text_color)
    p.drawCentredString(width - 210, 100, "Sk. Faisal Ahmed")

    p.setFont("Times-Italic", 14)
    p.setFillColor(colors.gray)
    p.drawCentredString(width - 210, 80, "CEO, Institute of Bioinformatics & AI")

    # Certificate ID (bottom-left corner)
    p.setFont("Courier-Bold", 12)
    p.setFillColor(colors.HexColor("#555555"))
    p.drawString(60, 50, f"Certificate ID: {course_progress.certificate_id}")

    # 🔹 Add QR Code (bottom-right corner)
    verify_url = request.build_absolute_uri(f"/course/certificate/{certificate_id}/")

    qr = qrcode.make(verify_url)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # Convert to ImageReader for ReportLab
    qr_image = ImageReader(qr_buffer)

    qr_size = 100
    p.drawImage(qr_image, 50, 70, width=qr_size, height=qr_size, mask='auto')

    # Label under QR
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.gray)
    p.drawCentredString(100, 65, "Scan to Verify")

    # Footer with website
    p.setFont("Helvetica-Oblique", 12)
    p.setFillColor(colors.HexColor("#888888"))
    p.drawCentredString(600, 50, "www.ibai.com | © Institute of Bioinformatics and Artificial Intelligence")

    # Finalize PDF
    p.showPage()
    p.save()
    return response




def verify_certificate(request):
    
    if request.method == 'GET' and 'certificate_id' in request.GET:
        certificate_id = request.GET.get('certificate_id')
        course_progress = get_object_or_404(CourseProgress, certificate_id=certificate_id)
        if course_progress:
            return redirect('reportlab_certificate', certificate_id=certificate_id)
        else:
            messages.error(request, "Invalid Certificate ID.")
            return render(request, 'courses/verify_certificate.html')
    else:
        return render(request, 'courses/verify_certificate.html')
    




