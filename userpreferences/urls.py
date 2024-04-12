from . import views
from django.urls import path
from .views import delete_user

urlpatterns = [
    path("", views.index, name="preferences"),
    path('delete-account/', delete_user, name='delete-account'),
    path('account/', views.account, name='useraccount'),
]
