from django.db import models
from django.utils.translation import gettext_lazy as _

class Role(models.TextChoices):
    ADMIN = "ADMIN", _("admin")
    EMPLOYEE = "EMPLOYEE", _("employee")
    GUEST = "GUEST", _("guest")
class TableStatus(models.TextChoices):
    AVAILABLE  = "AVAILABLE", _("available")
    RESERVED  = "Reserved ", _("reserved")
    HIDDEN = "HIDDEN", _("hidden")    