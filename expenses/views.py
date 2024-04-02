from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
# ! for post and get requests


@login_required(login_url="/authentication/login")
def index(request):
    categories = Category.objects.all()
    return render(request, "expenses/index.html")


def add_expense(request):
    categories = Category.objects.all()
    context = {
        "categories": categories,
        "values": request.POST
    }

    if request.method == "GET":
        return render(request, "expenses/add_expense.html", context)

    if request.method == "POST":
        # amount
        amount = request.POST["amount"]
        if not amount:
            messages.error(request, "Amount is required!")
            return render(request, "expenses/add_expense.html", context)

        # description, date, category
        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]
        if not description:
            messages.error(request, "Description is required!")
            return render(request, "expenses/add_expense.html", context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, "Expense Saved Successfully :)")

        return redirect("expenses")
