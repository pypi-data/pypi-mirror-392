from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdminTrapConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_admin_trap"
    verbose_name = _("Admin Trap")
