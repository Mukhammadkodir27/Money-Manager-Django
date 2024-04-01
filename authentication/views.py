from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.conf import settings
from django.contrib import auth
from django.urls import reverse
# ? from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import token_generator
from django.utils.encoding import force_str


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data["email"]
        if not validate_email(email):
            return JsonResponse({"email_error": "Email is invalid"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"email_error": "Sorry! this email already exists"}, status=409)
        return JsonResponse({"email_valid": True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data["username"]

        if not str(username).isalnum():
            return JsonResponse({"username_error": "username must only contain alphanumeric characters"}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({"username_error": "Sorry! this username already exists"}, status=409)
        return JsonResponse({"username_valid": True})


# ! email and registration part
class RegistrationView(View):
    def get(self, request):
        return render(request, "authentication/register.html")

    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # CREATE A USER ACCOUNT
        # ! registration part
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        context = {
            "fieldValues": request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password too short")
                    return render(request, "authentication/register.html", context)
                # ! email part
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                # * path to view
                # * getting domain we are on
                # * relative url to verification
                # * encode uid
                # * token

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse("activate", kwargs={
                    "uidb64": uidb64, "token": token_generator.make_token(user)
                })

                activate_link = "https://"+domain+link

                email_subject = "Activate your account"
                email_body = f"Hi {user.username}. \n Please use this link to verify your account!\n {activate_link}"
                email = EmailMessage(
                    email_subject,
                    email_body,
                    "noreply@semicolon.com",
                    [email],
                )
                email.send(fail_silently=False)
                messages.success(request, "Account successfully created")
                return render(request, "authentication/register.html")

        return render(request, "authentication/register.html")


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            # ! fixed force_text to force_str as it has been removed from later Django Versions
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect("login"+"?message"+"User already activated")

            if user.is_active:
                return redirect("login")
            user.is_active = True
            user.save()

            messages.success(request, "Account activated successfully")
            return redirect("login")

        except Exception as ex:
            pass
        return redirect("login")


class LoginView(View):
    def get(self, request):
        return render(request, "authentication/login.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(
                        request, "Welcome, "+user.username+" you are now logged in to your account")

                messages.error(
                    request, "Account is not active, please check your email!")
                return render(request, "authentication/login.html")
            messages.error(request, "Invalid credentials, try again")
            return render(request, "authentication/login.html")
