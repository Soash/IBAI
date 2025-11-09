from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
import random
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from .models import CustomUser

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.warning(request, "Invalid username or password.")
    return render(request, 'users/login.html')

def user_registration(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        first_name = ''.join([c if c.isalpha() or c.isspace() else '' for c in first_name])
        first_name = ' '.join(word.capitalize() for word in first_name.split())
        
        email = request.POST.get('email')

        username = generate_username(first_name)
        password1 = generate_password()
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('user_registration')

        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
        )
        user.save()
        
        send_account_email(request, first_name, username, password1, email)
        
        messages.success(request, "Registration successful! Login credentials have been sent to your email.")
        return redirect('user_login')

    return render(request, 'users/register.html')

def user_logout(request):
    logout(request)
    return redirect('user_login')

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            new_password = generate_password()
            user.set_password(new_password)
            user.save()
            send_account_email(request, user.first_name, user.username, new_password, email)
            messages.success(request, "Login credentials have been sent to your email.")
        except CustomUser.DoesNotExist:
            messages.warning(request, "No user found with this email address.")
    return render(request, 'users/password-reset.html')

def generate_username(first_name):
    username = first_name.lower().replace(" ", "")
    if CustomUser.objects.filter(username=username).exists():
        username = username + "{:03d}".format(random.randint(1, 999))
        return generate_username(username)
    return username

def generate_password(length=8):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def send_account_email(request, first_name, username, password1, email):
        login_url = request.build_absolute_uri('/login/')
        html_content = render_to_string('users/mail-signup.html', {
            'first_name': first_name,
            'username': username,
            'password': password1,
            'login_url': login_url,
            'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        })
        
        # Send only HTML email
        email_message = EmailMessage(
            subject="IBAI - Account Credentials",
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email_message.content_subtype = "html"
        email_message.send(fail_silently=False)

