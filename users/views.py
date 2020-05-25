import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from .forms import (ProfileUpdateForm, UserRegisterForm, UserTimeZoneForm,
                    UserUpdateForm)


def register(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already logged in")
        return redirect("todo-home")

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Your account has been created. You can now login.")

            # Creating a respective directory that belongs to this user
            os.mkdir(
                f"{settings.MEDIA_ROOT}/users/{username}_{form.instance.pk}")

            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
        tz_form = UserTimeZoneForm(request.POST)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

        if tz_form.is_valid():
            tz_form.full_clean()

            tz = tz_form.cleaned_data.get("timezone")
            request.user.profile.timezone = tz
            request.user.save()

        messages.success(request, f"Your account has been updated!")
        return redirect("profile")

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        tz_form = UserTimeZoneForm({"timezone": request.user.profile.timezone})

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "tz_form": tz_form
    }

    return render(request, "users/profile.html", context)
