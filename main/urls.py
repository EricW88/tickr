from django.shortcuts import redirect
from django.urls import path

from . import views

urlpatterns = [
    path("", views.homeRedirect),
    path("register/", views.registerPage, name="registerPage"),
    path("login/", views.loginPage, name="loginPage"),
    path("home/", views.homePage, name="homePage")
]