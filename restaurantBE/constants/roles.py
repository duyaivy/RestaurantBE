from django.db import models
from django.utils.translation import gettext_lazy as _

class Role(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    EMPLOYEE = "EMPLOYEE", _("Employee")
