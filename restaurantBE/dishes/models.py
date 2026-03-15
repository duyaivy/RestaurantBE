from restaurantBE.categories.models import Category
from restaurantBE.constants.choices import DishStatus
from django.db import models


class Dish(models.Model):
    name = models.JSONField(null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    description = models.JSONField(null=False)
    image = models.CharField(max_length=255, null=False)
    status = models.CharField(
        max_length=20, choices=DishStatus.choices, default=DishStatus.AVAILABLE
    )
    category_id = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, db_column="category_id"
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dish"

    def __str__(self):
        return f"Dish {self.id}"


class DishSnapshot(models.Model):
    name = models.JSONField(null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    description = models.JSONField(null=False)
    image = models.CharField(max_length=255, null=False)
    dish_id = models.ForeignKey(Dish, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dish_snapshot"

    def __str__(self):
        return f"DishSnapshot {self.id}"
