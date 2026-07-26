from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..models import User

def register_view(request):
    errors = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if not username:
            errors['username'] = 'Username is required.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username is already taken.'
            
        if not email:
            errors['email'] = 'Email is required.'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email is already registered.'
            
        if not password:
            errors['password'] = 'Password is required.'
            
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'

        if errors:
            return render(request, 'auth/register_page.html', {'errors': errors, 'data': request.POST})
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            profile_picture=profile_picture,
            phone=phone,
            address=address
        )
        user.save()
        
        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('/login/')
        
    return render(request, 'auth/register_page.html')

def login_view(request):
    errors = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username:
            errors['username'] = 'Username is required.'
            
        if not password:
            errors['password'] = 'Password is required.'

        if errors:
            return render(request, 'auth/login_page.html', {'errors': errors, 'data': request.POST})
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'auth/login_page.html', {'errors': errors, 'data': request.POST})
        
    return render(request, 'auth/login_page.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('/login/')