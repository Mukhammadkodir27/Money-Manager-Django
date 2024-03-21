from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "expenses/index.html")


def add_expenses(request):
    return render(request, "expenses/add_expense.html")
