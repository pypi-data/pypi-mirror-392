import time
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views import generic

from .forms import AdminTrapForm


class AdminTrapLogoutView(generic.View):
    """
    Handles logout functionality with perfect Django admin behavior mimicry.

    Important: This view only processes POST requests for actual logout.
    GET requests redirect to the admin index to maintain the trap illusion.
    """

    def post(self, request, *args, **kwargs):
        # Only process logout for authenticated users via POST
        if request.user.is_authenticated:
            from django.contrib.auth import logout

            logout(request)

            # Render logout confirmation page with admin context
            admin_site_context = AdminSite().each_context(request)
            context = {
                **admin_site_context,
                "title": _("Logged out"),
                "site_title": admin_site_context.get(
                    "site_title", _("Django administration")
                ),
                "site_header": admin_site_context.get(
                    "site_header", _("Django administration")
                ),
                # has_permission is False on logout page (matches Django admin)
                "has_permission": False,
            }
            return render(request, "admin_trap/logged_out.html", context)

    def get(self, request, *args, **kwargs):
        # GET requests redirect to admin index to maintain trap consistency
        return HttpResponseRedirect(reverse("admin_trap:index"))


class AdminTrapLoginView(generic.FormView):
    """
    Main login trap view that perfectly mimics Django admin login behavior.

    This view handles all admin paths and redirects them to the fake login page
    with proper next parameter handling, exactly like the real Django admin.
    """

    template_name = "admin_trap/login.html"
    form_class = AdminTrapForm
    start_time = None

    def dispatch(self, request, *args, **kwargs):
        self.start_time = time.time()

        # Ensure URLs end with trailing slash (Django admin behavior)
        if not request.path.endswith("/"):
            return redirect(f"{request.path}/", permanent=True)

        login_url = reverse("admin_trap:login")

        # If already on login page, proceed with normal form handling
        if request.path == login_url:
            return super().dispatch(request, *args, **kwargs)

        # All other admin paths redirect to login with next parameter
        next_url = request.get_full_path()

        # Security check: ensure next URL is safe
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
            next_url = reverse("admin_trap:index")

        return redirect_to_login(next_url, login_url)

    def get_form_kwargs(self):
        """Pass request to form for context-aware validation."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        """Build template context that matches real Django admin exactly."""
        context = super().get_context_data(**kwargs)

        # Admin site context for perfect visual mimicry
        admin_site_context = AdminSite().each_context(self.request)

        # Get username for personalized login display (like real admin)
        username = None
        if self.request.user.is_authenticated:
            username = self.request.user.get_username()

        # Handle next URL parameter with security validation
        next_url = self.request.GET.get(REDIRECT_FIELD_NAME, "")
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
            next_url = reverse("admin_trap:index")

        context.update(
            {
                **admin_site_context,
                "app_path": self.request.get_full_path(),
                REDIRECT_FIELD_NAME: next_url,
                "title": _("Log in"),
                "subtitle": None,  # Consistent with Django admin template
                "site_title": admin_site_context.get(
                    "site_title", _("Django administration")
                ),
                "site_header": admin_site_context.get(
                    "site_header", _("Django administration")
                ),
                # User context for template personalization
                "user": self.request.user,
                "username": username,
            }
        )

        return context

    def form_valid(self, form):
        """
        Form validation always fails to maintain the trap.

        Note: This method should never be reached since AdminTrapForm
        always raises ValidationError in clean(). Included for completeness.
        """
        return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Handle invalid form submission.

        Relies on AdminTrapForm.clean() which always raises ValidationError
        with the exact Django admin error message for failed logins.
        """
        return super().form_invalid(form)
