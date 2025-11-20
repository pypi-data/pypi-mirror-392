from django.urls import path, re_path
from . import views

app_name = "admin_trap"

urlpatterns = [
    # Login page - the main trap
    path("login/", views.AdminTrapLoginView.as_view(), name="login"),
    # Logout page - separate view for clean logout handling
    path("logout/", views.AdminTrapLogoutView.as_view(), name="logout"),
    # Catch-all pattern for any admin URL - redirects to login trap
    re_path(r"^.*$", views.AdminTrapLoginView.as_view(), name="index"),
]
