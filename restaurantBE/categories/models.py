from django.db import models
from rest_framework import serializers


class Category(models.Model):
    """
    Table Category model for organizing tables into different categories
    """

    name = models.JSONField(max_length=255, null=False, blank=False)
    description = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name["en"] if isinstance(self.name, dict) else str(self.name)


class CategoryBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
