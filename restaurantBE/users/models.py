from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password

from restaurantBE.roles.models import Role


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, name, email, password, **extra_fields):
        if not name:
            raise ValueError("The Name field must be set")

        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        # hash the password
        hashed_password = make_password(password)
        user.password = hashed_password
        user.save(using=self._db)
        return user

    def create_user(self, name, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(name, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{"email__iexact": username})


class User(AbstractUser):
    # remove not used fields
    username = None
    first_name = None
    last_name = None

    name = models.CharField(_("name"), max_length=150)
    email = models.EmailField(_("email"), unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
