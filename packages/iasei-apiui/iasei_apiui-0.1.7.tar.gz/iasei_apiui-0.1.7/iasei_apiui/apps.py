from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VueSwaggerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "iasei_apiui"
    verbose_name = _("iasei_apiui")
