from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
from django.views import View
from django.contrib.auth import logout
from django.http import HttpResponse


@login_required
def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, "currencies.json")

    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({"name": k, "value": v})

    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None

    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)
    else:
        default_currency = "USD"

    if request.method == "GET":
        return render(request, "preferences/index.html", {"currencies": currency_data, "user_preferences": user_preferences})
    else:
        # Use .get for safer dict access
        currency = request.POST.get("currency") or default_currency
        if currency:  # Ensure a currency was selected
            if exists:
                user_preferences.currency = currency
                user_preferences.save()
            else:
                UserPreference.objects.create(
                    user=request.user, currency=currency)
            messages.success(request, "Changes saved!")
        else:
            messages.error(request, "Please select a currency.")

        # Redirect to avoid double POST on refresh
        return render(request, "preferences/index.html", {"currencies": currency_data, "user_preferences": user_preferences})


def account(request):
    return render(request, "preferences/useraccount.html")


def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # This deletes the user
        logout(request)  # This logs out the user
        # Redirect to the homepage or a page indicating successful deletion
        return redirect('login')
    else:
        return HttpResponse("Not allowed", status=405)
