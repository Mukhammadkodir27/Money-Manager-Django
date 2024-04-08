from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages


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
