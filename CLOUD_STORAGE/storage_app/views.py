from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.http import HttpResponseForbidden
from .models import UserFile
from .azure_storage import upload_to_azure, delete_from_azure
from django.contrib.auth import logout
from django.contrib import messages
from django import forms
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
import uuid

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean_username(self):
        email = self.cleaned_data.get('username')
        try:
            user = User.objects.get(email=email)
            return user.username
        except User.DoesNotExist:
            raise forms.ValidationError('No user found with this email address.')

def register(request):
    if request.method == 'POST':
        if 'otp_verify' in request.POST:
            # Check if OTP has expired (10 minutes)
            timestamp = request.session.get('otp_timestamp')
            if timestamp and timezone.now().timestamp() - float(timestamp) > 600:  # 10 minutes
                messages.error(request, 'OTP has expired. Please try again.')
                request.session.pop('register_otp', None)
                request.session.pop('user_data', None)
                request.session.pop('otp_timestamp', None)
                return redirect('register')
                
            # Step 2: Verify OTP
            otp = request.POST.get('otp')
            stored_otp = request.session.get('register_otp')
            user_data = request.session.get('user_data')
            
            if not stored_otp or not user_data:
                messages.error(request, 'Registration session expired. Please try again.')
                return redirect('register')
            
            if otp == stored_otp:
                # Create user account
                form = CustomUserCreationForm(user_data)
                if form.is_valid():
                    user = form.save()
                    login(request, user)
                    
                    # Clear session data
                    request.session.pop('register_otp', None)
                    request.session.pop('user_data', None)
                    request.session.pop('otp_timestamp', None)
                    
                    messages.success(request, "Registration successful! Welcome to Echo.")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid form data. Please try again.")
                    return redirect('register')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return render(request, 'registration/register.html', {'step': 'verify'})
                
        else:
            # Step 1: Initial registration
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                # Don't save the form yet
                email = form.cleaned_data.get('email')
                
                # Generate and send OTP
                otp = generate_otp()  # Use the existing generate_otp function
                
                # Store form data and OTP in session
                request.session['user_data'] = request.POST
                request.session['register_otp'] = otp
                request.session['otp_timestamp'] = timezone.now().timestamp()
                
                # Send OTP email
                send_registration_otp_email(email, otp)
                
                messages.success(request, "Please check your email for OTP verification.")
                return render(request, 'registration/register.html', {'step': 'verify'})
            else:
                return render(request, 'registration/register.html', {'form': form, 'step': 'register'})
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form, 'step': 'register'})

def send_registration_otp_email(email, otp):
    """Send OTP for registration verification"""
    subject = 'Echo Registration OTP'
    message = f'''
    Thank you for registering with Echo!
    Your OTP for registration is: {otp}

    This OTP will expire in 10 minutes.

    
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )

# @login_required
# def dashboard(request):
#     files = UserFile.objects.filter(user=request.user).order_by('-uploaded_at')
#     return render(request, 'storage/dashboard.html', {'files': files})


@login_required
def dashboard(request):
    files = UserFile.objects.filter(user=request.user).order_by('category', '-uploaded_at')
    return render(request, 'storage/dashboard.html', {'files': files})

# @login_required
# def upload_file(request):
#     if request.method == 'POST':
#         if 'file' in request.FILES:
#             file = request.FILES['file']
            
#             # Upload to Azure
#             file_url = upload_to_azure(file, request.user.id)
            
#             # Save file info to database
#             UserFile.objects.create(
#                 user=request.user,
#                 file_name=file.name,
#                 file_url=file_url,
#                 file_size=file.size,
#                 file_type=file.content_type
#             )
            
#             messages.success(request, f"File '{file.name}' successfully uploaded!")
#             return redirect('dashboard')
#         else:
#             messages.error(request, "No file selected.")
    
#     return render(request, 'storage/upload.html')




@login_required
def upload_file(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            
            # Upload to Azure with username for folder structure
            file_url, category = upload_to_azure(file, request.user.id, request.user.username)
            
            # Save file info to database
            UserFile.objects.create(
                user=request.user,
                file_name=file.name,
                file_url=file_url,
                file_size=file.size,
                file_type=file.content_type,
                category=category  # Store the category
            )
            
            messages.success(request, f"File '{file.name}' successfully uploaded to your {category} folder!")
            return redirect('dashboard')
        else:
            messages.error(request, "No file selected.")
    
    return render(request, 'storage/upload.html')
@login_required
def delete_file(request, file_id):
    file = get_object_or_404(UserFile, id=file_id)
    
    # Check if the file belongs to the current user
    if file.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this file.")
    
    # Delete from Azure
    delete_from_azure(file.file_url)
    
    # Delete from database
    file.delete()
    
    messages.success(request, f"File '{file.file_name}' successfully deleted!")
    return redirect('dashboard')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'user/profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/change_password.html', {'form': form})

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send OTP to user's email"""
    subject = 'Echo Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}\n\nThis OTP will expire in 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            # Store OTP in session
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            request.session['otp_timestamp'] = timezone.now().timestamp()
            
            # Send OTP via email
            send_otp_email(email, otp)
            
            messages.success(request, 'OTP has been sent to your email address.')
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
    
    return render(request, 'registration/forgot_password.html', {'step': 'email'})

def verify_otp(request):
    if 'reset_otp' not in request.session:
        messages.error(request, 'Please request an OTP first.')
        return redirect('forgot_password')
    
    # Check if OTP has expired (10 minutes)
    timestamp = request.session.get('otp_timestamp')
    if timestamp and timezone.now().timestamp() - float(timestamp) > 600:  # 10 minutes
        messages.error(request, 'OTP has expired. Please request a new one.')
        del request.session['reset_otp']
        del request.session['reset_email']
        del request.session['otp_timestamp']
        return redirect('forgot_password')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        
        if otp == stored_otp:
            # Clear OTP from session
            del request.session['reset_otp']
            del request.session['otp_timestamp']
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'registration/forgot_password.html', {'step': 'verify'})

def reset_password(request):
    if 'reset_email' not in request.session:
        messages.error(request, 'Please request an OTP first.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = SetPasswordForm(User.objects.get(email=request.session['reset_email']), request.POST)
        if form.is_valid():
            form.save()
            # Clear email from session
            del request.session['reset_email']
            messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
            return redirect('login')
    else:
        form = SetPasswordForm(User.objects.get(email=request.session['reset_email']))
    
    return render(request, 'registration/forgot_password.html', {'form': form, 'step': 'reset'})

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
            return redirect('dashboard')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})