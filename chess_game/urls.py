from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "", include("chess_online.urls")
    ),  # Это сделает пустой URL перенаправлением на приложение chess_online
    path("chess/", include("chess_online.urls")),  # Пути нашего приложения для шахмат
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "accounts/", include("django.contrib.auth.urls")
    ),  # Включение стандартных маршрутов аутентификации
]
