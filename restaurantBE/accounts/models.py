from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password


class AccountManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email là bắt buộc")
        if not name:
            raise ValueError("Tên là bắt buộc")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(email, name, password, **extra_fields)


class Account(AbstractUser):
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=[
            ("admin", "ADMIN"),
            ("employee", "EMPLOYEE"),
        ],
    )
    avatar = models.CharField(max_length=255, blank=True, null=True)
    owner_id = models.IntegerField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    objects = AccountManager()

    class Meta:
        db_table = "Account"

    def __str__(self):
        return self.email
