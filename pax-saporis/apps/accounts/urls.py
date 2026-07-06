from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.current_user, name="current_user"),
    path("csrf/", views.get_csrf_token, name="csrf"),
]
