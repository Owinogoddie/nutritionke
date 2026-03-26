from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileSetupForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Let's set up your profile.")
            return redirect('accounts:setup_profile')
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect('accounts:login')


@login_required
def setup_profile(request):
    """
    Profile setup shown right after registration.
    User fills in age, weight, height, goal, health conditions.
    """
    form = ProfileSetupForm(request.POST or None, instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.profile_complete = True
            user.save()
            messages.success(request, "Profile set up! Your personalised plan is ready.")
            return redirect('dashboard:home')

    return render(request, 'accounts/setup_profile.html', {'form': form})


@login_required
def profile_view(request):
    """
    Read-only profile page showing all user info and calculated targets.
    """
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def edit_profile_view(request):
    """
    Edit profile page. Handles name, avatar, and all ProfileSetupForm fields.
    Recalculates nutrition targets on save.
    """
    form = ProfileSetupForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        # Handle name fields (not part of ProfileSetupForm)
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if form.is_valid():
            user = form.save(commit=False)

            # Update name
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name

            # Handle avatar upload
            if request.FILES.get('avatar'):
                user.avatar = request.FILES['avatar']

            user.profile_complete = True
            user.save()  # triggers calculate_targets() via User.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, 'accounts/edit_profile.html', {'form': form, 'user': request.user})