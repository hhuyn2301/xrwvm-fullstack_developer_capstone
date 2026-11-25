"""Django API, admin and React page routes."""
from django.contrib import admin
from django.urls import include, path
from djangoapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("djangoapp/", include("djangoapp.urls")),
    path("health", views.health),
    path("", views.frontend),
    path("dealers", views.frontend),
    path("login", views.frontend),
    path("register", views.frontend),
    path("signup", views.frontend),
    path("about", views.frontend),
    path("contact", views.frontend),
    path("dealer/<int:dealer_id>", views.frontend),
    path("postreview/<int:dealer_id>", views.frontend),
]
